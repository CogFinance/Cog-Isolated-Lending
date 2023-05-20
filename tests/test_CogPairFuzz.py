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
    ratio = st.floats(min_value=0.1, max_value=0.9)

    def __init__(self):
        super().__init__()
        oracle.setPrice(asset_one_coin_price, sender=account)
        oracle.setUpdated(True, sender=account)
        cog_pair.get_exchange_rate(sender=account)


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
            self.cog_pair.redeem(account, amt, sender=account)

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
        amt = amt * self.SCALE
        if self.cog_pair.user_collateral_share(account) > 0:
            amt = min(amt, self.cog_pair.user_collateral_share(account))
            self.cog_pair.borrow(account, amt, sender=account)

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

    @invariant()
    def true(self):
        assert True

def test_big_fuzz(cog_pair, asset, collateral, accounts, oracle):
    # Injects current context into the state machine
    for k, v in locals().items():
        setattr(CogPairFuzz, k, v)

    CogPairFuzz.TestCase.settings = settings(max_examples=5, stateful_step_count=30, deadline=timedelta(milliseconds=5000))
    run_state_machine_as_test(CogPairFuzz)