import boa
import pytest

from datetime import timedelta

from hypothesis import (
    given,
    settings,
    strategies as st,
)

from tests.fixtures import *


@given(
    amount=st.integers(min_value=100000, max_value=2**128),
)
@settings(max_examples=10, deadline=None)
def test_add_collateral(cog_pair, amount, accounts, collateral):
    account = accounts[0]

    collateral.mint(account, amount, sender=account)
    collateral.approve(cog_pair, amount, sender=account)

    old_total_collateral_share = cog_pair.total_collateral_share()

    old_balance = collateral.balanceOf(account)
    before_balance = cog_pair.user_collateral_share(account)


    cog_pair.add_collateral(account, amount, sender=account)
    after_balance_0 = cog_pair.user_collateral_share(account)


    new_balance = collateral.balanceOf(account)

    # Tokens from the user are transferred from the depositor equal to the amount they called with.
    assert old_balance == new_balance + amount

    # Test Invariant `user_collateral_share[to]` is set equal to `user_collateral_share[to] + amount`.
    assert after_balance_0 == before_balance + amount
    assert after_balance_0 > before_balance

    # Test Invariant `totalCollateralShare` is set equal to `old_total_collateral_share + amount`.
    assert cog_pair.total_collateral_share() == old_total_collateral_share + amount
    
    account_2 = accounts[1]

    collateral.mint(account_2, amount, sender=account_2)
    collateral.approve(cog_pair, amount, sender=account_2)
    old_balance = collateral.balanceOf(account_2)

    old_total_collateral_share = cog_pair.total_collateral_share()
    before_balance = cog_pair.user_collateral_share(account_2)
    cog_pair.add_collateral(account_2, amount, sender=account_2)

    new_balance = collateral.balanceOf(account_2)
    after_balance_1 = cog_pair.user_collateral_share(account_2)

    # Test Invariant Tokens from the user are transferred from the depositor equal to the amount they called with.
    assert old_balance == new_balance + amount

    # Test Invariant `user_collateral_share[to]` is set equal to `user_collateral_share[to] + amount`.
    assert after_balance_1 == before_balance + amount
    assert after_balance_1 > before_balance    

    # Test Invariant `total_collateral_share` is set equal to `oldTotalCollateralShare + share`.
    assert cog_pair.total_collateral_share() == old_total_collateral_share + amount

    collateral.approve(cog_pair, amount*10, sender=account_2)
    with boa.reverts():
        # Test invariant This function should revert if the user does not have sufficient funds.
        cog_pair.add_collateral(account, amount*10, sender=account_2)

@given(
    amount=st.integers(min_value=100000, max_value=2**128),
)
@settings(max_examples=10, deadline=None)
def test_remove_collateral(cog_pair, amount, accounts, collateral):
    # Moslty irrelevant to the test, but we need to mint some collateral to the accounts
    # so that we can remove it.
    account = accounts[0]
    collateral.mint(account, amount, sender=account)
    collateral.approve(cog_pair, amount, sender=account)
    cog_pair.add_collateral(account, amount, sender=account)

    account_2 = accounts[1]
    collateral.mint(account_2, amount, sender=account_2)
    collateral.approve(cog_pair, amount, sender=account_2)
    cog_pair.add_collateral(account_2, amount, sender=account_2)

    # Next we can actually test that collateral is removed properly
    old_balance = collateral.balanceOf(account)
    before_balance = cog_pair.user_collateral_share(account)
    old_total_collateral_share = cog_pair.total_collateral_share()

    cog_pair.remove_collateral(account, amount, sender=account)

    after_balance_0 = cog_pair.user_collateral_share(account)

    new_balance = collateral.balanceOf(account)

    # The collateral token contract is called, transferring the amount of collateral to the specified address
    assert new_balance == old_balance + amount

    # Test `user_collateral_share[msg.sender]` is set equal to `user_collateral_share[msg.sender] - share`.
    assert after_balance_0 == before_balance - amount

    # Test `total_collateral_share` is set equal to `total_collateral_share - share`
    assert cog_pair.total_collateral_share() == old_total_collateral_share - amount

    with boa.reverts():
        # Test Invariant The function should not allow a user to withdraw more collateral than they own
        cog_pair.remove_collateral(account, amount*10, sender=account)

def test_cannot_remove_when_insolvent(cog_pair, accounts, collateral, asset, oracle):
    # Invariant The function should revert if the user would become insolvent
    # TODO: This should probably fuzz
    # This scenario is a little more tricky so requires its own test
    account = accounts[0]
    asset_one_coin_price = 1000000000000000000
    assets_available = 90000000000000000000000000000

    oracle.setPrice(asset_one_coin_price, sender=account)
    oracle.setUpdated(True, sender=account)
    cog_pair.get_exchange_rate(sender=account)

    # Add assets to be borrowed
    account_2 = accounts[1]
    asset.mint(account_2, assets_available, sender=account_2)
    asset.approve(cog_pair, assets_available, sender=account_2)
    cog_pair.deposit(assets_available, account_2, sender=account_2)


    collateral.mint(account, asset_one_coin_price, sender=account)
    collateral.approve(cog_pair, asset_one_coin_price, sender=account)
    cog_pair.add_collateral(account, asset_one_coin_price, sender=account)

    cog_pair.borrow(740000000000000000, sender=account)

    with boa.reverts():
        cog_pair.remove_collateral(account, asset_one_coin_price-1000000, sender=account)
