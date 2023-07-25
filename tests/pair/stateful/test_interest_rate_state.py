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

import boa


MINT_AMOUNT = 100*10**18
BORROW = 1
REPAY = 2
COLLATERALIZATION_RATE_PCT = 75  # 75%
NUM_STEPS = 100


class StateMachine(RuleBasedStateMachine):
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
        to_borrow = int(amount * (collateral_amount * collat_rate // 100 - amount_owed))

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

    @rule(percent=st.floats(min_value=-0.5, max_value=0.5))
    def nudge_oracle(self, percent):
        current_price = self.oracle.get()[1]
        new_price = int((1 + percent/100) * current_price)
        with boa.env.prank(self.accounts[0]):
            self.oracle.setPrice(new_price)

    @rule(dt=time_shift)
    def time_travel(self, dt):
        boa.env.time_travel(dt)


def test_state_machine_isolation(accounts, collateral, asset, oracle, cog_pair):
    for k, v in locals().items():
        setattr(StateMachine, k, v)

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


    StateMachine.settings = {
        "stateful_step_count": NUM_STEPS,
        "suppress_health_check": list(HealthCheck),
    }
    run_state_machine_as_test(StateMachine)
