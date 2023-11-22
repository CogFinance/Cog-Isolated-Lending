import boa
import pytest

from datetime import timedelta

from hypothesis import (
    given,
    settings,
    strategies as st,
)

# Most mission critical logic for borrow actually exists in accrue, and is best tested there

def test_borrow_medium_invariants(cog_pair, collateral, accounts, asset, oracle):
    # Initial setup
    account = accounts[0]
    asset_one_coin_price = 1000000000000000000
    
    amount = 1000 * (10 ** 18)

    oracle.setPrice(asset_one_coin_price, sender=account)
    oracle.setUpdated(True, sender=account)
    cog_pair.get_exchange_rate(sender=account)

    asset.mint(account, amount, sender=account)
    asset.approve(cog_pair, amount, sender=account)
    cog_pair.deposit(amount, account, sender=account)

    # Borrow
    (old_elastic, old_base) = cog_pair.total_borrow()
    account = accounts[1]

    with boa.reverts("Insufficient Collateral"):
        cog_pair.borrow(amount, accounts[3], account, sender=accounts[3])

    collateral.mint(account, amount*10, sender=account)
    collateral.approve(cog_pair, amount*10, sender=account)
    cog_pair.add_collateral(account, amount*10, sender=account)

    old_borrow_part = cog_pair.user_borrow_part(account)

    amount = 100 * (10 ** 18)

    # BORROW_OPENING_FEE and BORROW_OPENING_FEE_PRECISION both respectively
    fee = int((amount * 50) / 100000)

    cog_pair.borrow(amount, sender=account)    

    # Test Invariant `user_borrow_part[account]` is set equal to `user_borrow_part[account] + amount`.
    assert cog_pair.user_borrow_part(account) == old_borrow_part + amount + fee

    # Test Invariant `total_borrow` is set equal to `total_borrow + amount`.
    (_, current_base) = cog_pair.total_borrow()
    assert  current_base == old_base + amount + fee

    account = accounts[1]

    (old_elastic, old_base) = cog_pair.total_borrow()
    old_borrow_part = cog_pair.user_borrow_part(account)

    collateral.mint(account, amount*10, sender=account)
    collateral.approve(cog_pair, amount*10, sender=account)
    cog_pair.add_collateral(account, amount*10, sender=account)

    old_borrow_part = cog_pair.user_borrow_part(account)

    amount = 100 * (10 ** 18)

    # BORROW_OPENING_FEE and BORROW_OPENING_FEE_PRECISION both respectively
    fee = int((amount * 50) / 100000)

    cog_pair.borrow(amount, sender=account)    

    # Test Invariant `user_borrow_part[account]` is set equal to `user_borrow_part[account] + amount`.
    assert cog_pair.user_borrow_part(account) == old_borrow_part + amount + fee

    # Test Invariant `total_borrow` is set equal to `total_borrow + amount`.
    (_, current_base) = cog_pair.total_borrow()
    assert  current_base == old_base + amount + fee

def test_borrow_checks_proper_account(cog_pair, collateral, accounts, asset, oracle):
    # Initial setup
    account = accounts[0]
    asset_one_coin_price = 1000000000000000000
    
    amount = 1000 * (10 ** 18)

    oracle.setPrice(asset_one_coin_price, sender=account)
    oracle.setUpdated(True, sender=account)
    cog_pair.get_exchange_rate(sender=account)

    asset.mint(account, amount, sender=account)
    asset.approve(cog_pair, amount, sender=account)
    cog_pair.deposit(amount, account, sender=account)

    # Borrow
    account = accounts[2]
    cog_pair.approve_borrow(accounts[1], 2 ** 256 -1, sender=account)

    account = accounts[1]

    collateral.mint(account, amount*10, sender=account)
    collateral.approve(cog_pair, amount*10, sender=account)
    cog_pair.add_collateral(account, amount*10, sender=account)

    with boa.reverts("Insufficient Collateral"):
        cog_pair.borrow(amount, accounts[2], account, sender=account)

def test_cannot_borrow_more_than_allowed(cog_pair, collateral, accounts, asset, oracle):
    account = accounts[0]

    asset_one_coin_price = 1000000000000000000
    amount = 1000 * (10 ** 18)

    oracle.setPrice(asset_one_coin_price, sender=account)
    oracle.setUpdated(True, sender=account)
    cog_pair.get_exchange_rate(sender=account)
   
    collateral.mint(account, amount*10, sender=account)
    collateral.approve(cog_pair, amount*10, sender=account)
    cog_pair.add_collateral(account, amount*10, sender=account)

    cog_pair.approve_borrow(accounts[1], amount, sender=account)

    account = accounts[1]
    
    with boa.reverts():
        cog_pair.borrow(amount+1, accounts[0], account, sender=account)

