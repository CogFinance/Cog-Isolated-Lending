import ape

import pytest

from datetime import timedelta

from hypothesis import settings
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, run_state_machine_as_test, rule, invariant

from tests.fixtures import (
    account,
    collateral,
    asset,
    oracle,
    cog_pair_blueprint,
    cog_factory,
    cog_pair
)

class CogPairFuzz(RuleBasedStateMachine):
    user_id = st.integers(min_value=0, max_value=9)
    amount = st.integers(min_value=5, max_value=50)
    SCALE = 10 ** 18
    STARTING_PRICE = 10 * 10 ** 18
    ratio = st.floats(min_value=0.1, max_value=0.9)
    oracle_step = st.floats(min_value=-0.01, max_value=0.01)

    def __init__(self):
        super().__init__()
        account = self.accounts[0]
        self.oracle.setPrice(self.STARTING_PRICE, sender=account)
        self.oracle.setUpdated(True, sender=account)
        self.cog_pair.get_exchange_rate(sender=account)


    @rule(uid=user_id, amt = amount)
    def deposit(self, uid, amt):
        account = self.accounts[uid]
        amt = amt * self.SCALE
        self.asset.mint(account, amt, sender=account)
        self.asset.approve(self.cog_pair, amt, sender=account)
        self.cog_pair.deposit(amt, account, sender=account)

    @rule(uid=user_id, amt = amount)
    def withdraw(self, uid, amt):
        account = self.accounts[uid]
        amt = amt * self.SCALE
        if self.cog_pair.balanceOf(account) > 0:
            amt = min(amt, self.cog_pair.balanceOf(account))
            amt = min(amt, self.cog_pair.maxWithdraw(account))
            self.cog_pair.withdraw(amt, account, sender=account)

    @rule(uid=user_id, amt = amount)
    def mint(self, uid, amt):
        account = self.accounts[uid]
        amt = amt * self.SCALE
        self.asset.mint(account, amt, sender=account)
        self.asset.approve(self.cog_pair, amt, sender=account)
        amt_in_shares = self.cog_pair.convertToAssets(amt)
        self.cog_pair.mint(amt_in_shares, account, sender=account)

    @rule(uid=user_id, amt = amount)
    def redeem(self, uid, amt):
        account = self.accounts[uid]
        amt = amt * self.SCALE
        if self.cog_pair.balanceOf(account) > 0:
            amt = min(amt, self.cog_pair.balanceOf(account))
            amt = min(amt, self.cog_pair.maxRedeem(account))
            self.cog_pair.redeem(amt, account, sender=account)

    @rule(uid=user_id, amt = amount)
    def add_collateral(self, uid, amt):
        account = self.accounts[uid]
        amt = amt * self.SCALE
        self.collateral.mint(account, amt, sender=account)
        self.collateral.approve(self.cog_pair, amt, sender=account)
        self.cog_pair.add_collateral(account, amt, sender=account)

    @rule(uid=user_id, amt = amount)
    def remove_collateral(self, uid, amt):
        account = self.accounts[uid]
        amt = amt * self.SCALE
        if self.cog_pair.user_collateral_share(account) > 0:
            amt = min(amt, self.cog_pair.user_collateral_share(account))
            self.cog_pair.remove_collateral(account, amt, sender=account)

    @rule(uid=user_id, amt = amount)
    def borrow(self, uid, amt):
        account = self.accounts[uid]
        cog_pair = self.cog_pair
        amt = amt * self.SCALE
        if cog_pair.user_collateral_share(account) > 0 and cog_pair.user_borrow_part(account) == 0:
            return_val = self.oracle.get()
            price = return_val[1]
            max_borrowable_amount = ((cog_pair.convertToAssets(cog_pair.user_collateral_share(account)) * price / 10 ** 18) * 0.73)
            if self.asset.balanceOf(cog_pair) > max_borrowable_amount:
                cog_pair.borrow(account, max_borrowable_amount, sender=account)

    @rule(uid=user_id, amt = amount)
    def repay(self, uid, amt):
        account = self.accounts[uid]
        amt = amt * self.SCALE
        if self.cog_pair.user_borrow_part(account) > 0:
            amt = min(amt, self.cog_pair.user_borrow_part(account))
            self.asset.mint(account, amt, sender=account)
            self.asset.approve(self.cog_pair, amt, sender=account)
            self.cog_pair.repay(account, amt, sender=account)

    @rule(uid=user_id)
    def accrue(self, uid):
        account = self.accounts[uid]
        self.cog_pair.accrue(sender=account)

    @rule(uid=user_id, step=oracle_step)
    def update_oracle(self, uid, step):
        account = self.accounts[uid]
        (_, current_price) = self.oracle.get()
        new_price = int(current_price + (current_price * step))
        self.oracle.setPrice(new_price, sender=account)

    @invariant()
    def true(self):
        assert True

def test_big_fuzz(cog_pair, asset, collateral, accounts, oracle):
    # Injects current context into the state machine
    for k, v in locals().items():
        setattr(CogPairFuzz, k, v)

    CogPairFuzz.TestCase.settings = settings(max_examples=5, stateful_step_count=50, deadline=timedelta(milliseconds=5000))
    run_state_machine_as_test(CogPairFuzz)