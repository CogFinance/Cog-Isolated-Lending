import pytest
import hypothesis.strategies as st
from hypothesis._settings import HealthCheck
from hypothesis.stateful import (
    RuleBasedStateMachine,
    initialize,
    invariant,
    rule,
    run_state_machine_as_test,
)
from hypothesis import settings
import boa


MINT_AMOUNT = 100*10**18
BORROW = 1
REPAY = 2
COLLATERALIZATION_RATE_PCT = 75  # 75%
NUM_STEPS = 100_000
COLLATERIZATION_RATE = 75000


class BigFuzz(RuleBasedStateMachine):
    # a strategy to generate a number which represents percent
    # of account to borrow or repay.
    amount = st.floats(min_value=0.01, max_value=0.99)
    user_id = st.integers(min_value=0, max_value=9)
    time_shift = st.integers(min_value=1, max_value=30 * 86400)

    @initialize()
    def setup(self):
        return

    @rule(user_id=user_id, amount=amount)
    def borrow(self, user_id, amount):
        user = self.accounts[user_id]
        self.cog_pair.accrue()
        collateral_amount = self.cog_pair.user_collateral_share(user)
        borrowed_amount = self.cog_pair.user_borrow_part(user)
        (elastic, base) = self.cog_pair.total_borrow()
        if base == 0:
            amount_owed = borrowed_amount
        else:
            amount_owed = int((borrowed_amount * elastic) // base)

        # borrowing exactly AT the collateralization ratio leads to "too little collateral"
        collat_rate = COLLATERALIZATION_RATE_PCT - 1
        to_borrow = int(amount * (collateral_amount * (collat_rate / 100) - amount_owed))

        if to_borrow <= 0:  # could be <0 if user is insolvent
            return

        if to_borrow > self.asset.balanceOf(self.cog_pair):
            to_borrow = self.asset.balanceOf(self.cog_pair)

        with boa.env.prank(user):
            self.cog_pair.borrow(to_borrow)


    @rule(user_id=user_id, amount=amount)
    def repay(self, user_id, amount):
        user = self.accounts[user_id]
        borrowed_amount = self.cog_pair.user_borrow_part(user)
        if borrowed_amount == 0:
            return
        (elastic, base) = self.cog_pair.total_borrow()

        assert elastic >= base

        # FWIW there are occasionally bugs where this amount is rounded
        # up, and fails to overpay, so we subtract 1
        to_repay = int((amount * borrowed_amount))
        to_repay = int(to_repay - 1)
        if to_repay <= 0:
            return

        if to_repay > base:
            # Sometimes the float conversions for amount
            # can cause some minor rounding issues and try to overpay
            to_repay = base

        with boa.env.prank(user):
            self.asset.mint(user, to_repay)
            self.asset.approve(self.cog_pair, to_repay)
            self.cog_pair.repay(user, to_repay)
        
            self.cog_pair.accrue()

    @rule(user_id=user_id, amount=amount)
    def add_collateral(self, user_id, amount):
        user = self.accounts[user_id]
        amount = int(amount * 10 ** 18)
        if amount + self.cog_pair.user_collateral_share(user) >= (2 ** 128):
            return

        with boa.env.prank(user):
            self.collateral.mint(user, amount)
            self.collateral.approve(self.cog_pair, amount)
            self.cog_pair.add_collateral(user, amount)


    @rule(user_id=user_id, amount=amount)
    def remove_collateral(self, user_id, amount):
        self.cog_pair.accrue()
        user = self.accounts[user_id] 
        collateral_amount = self.cog_pair.user_collateral_share(user)
        share = collateral_amount - (collateral_amount * amount)
        # Exchange Rate precision = 1e18, and collateralization_Rate_precision = 1e5
        collateral_amt = share * (10 ** 18 / 10 ** 5) * COLLATERIZATION_RATE

        (_, exchange_rate) = self.oracle.get()

        (total_borrow_elastic, total_borrow_base) = self.cog_pair.total_borrow()
        borrow_part = 0
        if total_borrow_elastic > 0: 
            borrow_part = self.cog_pair.user_borrow_part(user)
            borrow_part = borrow_part * total_borrow_elastic * exchange_rate / total_borrow_base

        if collateral_amt < borrow_part:
            return

        with boa.env.prank(user):
            self.cog_pair.remove_collateral(user, int(collateral_amount * amount))

    @rule(percent=st.floats(min_value=-0.5, max_value=0.5))
    def nudge_oracle(self, percent):
        current_price = self.oracle.get()[1]
        new_price = int((1 + percent) * current_price)
        with boa.env.prank(self.accounts[0]):
            self.oracle.setPrice(new_price)

    @rule(dt=time_shift)
    def time_travel(self, dt):
        boa.env.time_travel(dt)

    @rule()
    def liquidate_insolvent_users(self):
        self.cog_pair.accrue()
        (total_borrow_elastic, total_borrow_base) = self.cog_pair.total_borrow()
        if total_borrow_base == 0:
            return

        (_, exchange_rate) = self.oracle.get()

        for i in range(10):
            user = self.accounts[i]
            share = self.cog_pair.user_collateral_share(user)
            if share == 0:
                continue
            # Exchange Rate precision = 1e18, and collateralization_Rate_precision = 1e5
            collateral_amt = share * (1000000000000000000 / 100000) * 75000

            (total_borrow_elastic, total_borrow_base) = self.cog_pair.total_borrow()

            borrow_part = 0
            if total_borrow_elastic > 0: 
                borrow_part = self.cog_pair.user_borrow_part(user)
                borrow_part = ((borrow_part * total_borrow_elastic) * exchange_rate) / total_borrow_base
            
            if collateral_amt < borrow_part:
                liquidator = self.accounts[10]
                with boa.env.prank(liquidator):
                    self.asset.mint(liquidator, 100 * 10 ** 18)
                    self.asset.approve(self.cog_pair, 100 * 10 **18)
                    print(self.cog_pair.user_borrow_part(user))
                    self.cog_pair.liquidate(user, self.cog_pair.user_borrow_part(user), liquidator)
    
    @invariant()
    def interest_stays_within_bounds(self):
        self.cog_pair.accrue()
        
        (interest_per_second, last_accrued, fees_earned_fraction) = self.cog_pair.accrue_info()
        (total_borrow_elastic, total_borrow_base) = self.cog_pair.total_borrow()
        if total_borrow_base == 0:
            STARTING_INTEREST_PER_SECOND = 317097920
            assert interest_per_second == STARTING_INTEREST_PER_SECOND
    
        assert interest_per_second <= 31709792000
        assert interest_per_second >= 79274480

def test_state_machine_isolation(accounts, collateral, asset, oracle, cog_pair):
    for k, v in locals().items():
        setattr(BigFuzz, k, v)

    with boa.env.prank(accounts[0]):
        oracle.setPrice(10**18)
        oracle.setUpdated(True)

        asset.mint(boa.env.eoa, MINT_AMOUNT)
        asset.approve(cog_pair, MINT_AMOUNT)
        cog_pair.deposit(MINT_AMOUNT, boa.env.eoa)

        for account in accounts:
                collateral.mint(account, MINT_AMOUNT)

    for account in accounts:
        with boa.env.prank(account):
            collateral.approve(cog_pair, MINT_AMOUNT)
            cog_pair.add_collateral(account, MINT_AMOUNT)


    BigFuzz.TestCase.settings = settings(max_examples=5, stateful_step_count=15, deadline=None)
    run_state_machine_as_test(BigFuzz)

def test_user_gets_liquidated(accounts, collateral, asset, oracle, cog_pair):
    for k, v in locals().items():
        setattr(BigFuzz, k, v)

    with boa.env.prank(accounts[0]):
        oracle.setPrice(10**18)
        oracle.setUpdated(True)

        asset.mint(boa.env.eoa, 100 * 10**18)
        asset.approve(cog_pair, 100 * 10**18)
        cog_pair.deposit(100 * 10**18)

    with boa.env.anchor():
        state = BigFuzz()
        state.add_collateral(3, 0.05)
        state.borrow(3, 0.99)
    
        (elastic, base) = state.cog_pair.total_borrow()
        assert base != 0
        start_borrow_part = state.cog_pair.user_borrow_part(state.accounts[3])
        state.nudge_oracle(0.5)
        state.nudge_oracle(0.5)
        state.nudge_oracle(0.5)
        state.nudge_oracle(0.5)
        state.liquidate_insolvent_users()
        state.time_travel(86400 * 30)

        end_borrow_part = state.cog_pair.user_borrow_part(state.accounts[3])

        assert end_borrow_part < start_borrow_part
