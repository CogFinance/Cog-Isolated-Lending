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


class StateMachine(RuleBasedStateMachine):
    # a strategy to generate a number which represents percent
    # of account to borrow or repay.
    amount = st.floats(min_value=0, max_value=1)
    user_id = st.integers(min_value=0, max_value=9)

    @initialize()
    def setup(self):
        self.last_action = None  # 1 is BORROW, 2 is REPAY
        self.last_interest_info = None

    @rule(user_id=user_id, amount=amount)
    def borrow(self, user_id, amount):
        user = self.accounts[user_id]
        collateral_amount = self.cog_pair.user_collateral_share(user)
        borrowed_amount = self.cog_pair.user_borrow_part(user)

        # borrowing exactly AT the collateralization ratio leads to "too little collateral"
        collat_rate = COLLATERALIZATION_RATE_PCT - 1
        to_borrow = int(amount * (collateral_amount * collat_rate // 100 - borrowed_amount))

        if amount <= 0:  # could be <0 if user is insolvent
            return

        with boa.env.prank(user):
            self.cog_pair.borrow(user, to_borrow)

        self.last_action = BORROW
        self.last_interest_info = self.cog_pair.accrue_info()


    @rule(user_id=user_id, amount=amount)
    def repay(self, user_id, amount):
        user = self.accounts[user_id]
        borrowed_amount = self.cog_pair.user_borrow_part(user)

        to_repay = int(amount * borrowed_amount)

        self.last_action = REPAY
        self.last_interest_info = self.cog_pair.accrue_info()

        with boa.env.prank(user):
            self.cog_pair.repay(user, to_repay)


    @rule(percent=st.floats(min_value=-0.5, max_value=0.5))
    def nudge_oracle(self, percent):
        return  # stub

        current_price = self.oracle.get()[1]
        new_price = int((1 + percent/100) * current_price)
        with boa.env.prank(self.accounts[0]):
            self.oracle.setPrice(new_price)

    @invariant()
    def check_interest_rate_direction(self):
        if self.last_interest_info is None:
            return

        interest_rate_info = self.cog_pair.accrue_info()

        if self.last_action == REPAY:
            assert interest_rate_info[0] <= self.last_interest_info[0]
        elif self.last_action == BORROW:
            assert interest_rate_info[0] >= self.last_interest_info[0]
        else:
            # whoops, bug in test harness
            raise RuntimeError(f"unknown last_action: {self.last_action}")


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
        #"stateful_step_count": NUM_STEPS,
        "suppress_health_check": HealthCheck.all(),
    }
    run_state_machine_as_test(StateMachine)
