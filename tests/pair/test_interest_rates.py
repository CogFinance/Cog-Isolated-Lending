import pytest
import boa

from hypothesis import (
    given,
    settings,
    strategies as st,
)


ONE_PERCENT = 317097920 

def test_stable_interest_rate_maximum(cog_stable_pair, collateral, asset, accounts, account):
    cog_pair = cog_stable_pair

    asset.mint(account, 100 * 10 ** 18, sender=account)
    asset.approve(cog_pair, 100 * 10 ** 18, sender=account)
    cog_pair.deposit(100 * 10 ** 18, account, sender=account)

    account = accounts[1]

    collateral.mint(account, 1000 * 10 ** 18, sender=account)
    collateral.approve(cog_pair, 1000 * 10 ** 18, sender=account)
    cog_pair.add_collateral(account, 1000 * 10 ** 18, sender=account)

    (interest_per_second, last_accrued, fees_earned_fraction) = cog_pair.accrue_info()
    assert interest_per_second ==  ONE_PERCENT * 5
    cog_pair.borrow(1 * 10 ** 18, sender=account)

    boa.env.time_travel(86400 * 365)
    cog_pair.accrue(sender=account)

    (interest_per_second, last_accrued, fees_earned_fraction) = cog_pair.accrue_info()
    assert interest_per_second == ONE_PERCENT * 2
    cog_pair.borrow( 99 * 10 ** 18, sender=account)
    
    # Note to self, elasticity is low as shit so this should really be fixed
    boa.env.time_travel(86400 * 365 * 7)
    cog_pair.accrue(sender=account)
    (interest_per_second, last_accrued, fees_earned_fraction) = cog_pair.accrue_info()
    
    assert interest_per_second == ONE_PERCENT * 25

def test_low_interest_rate_maximum(cog_low_pair, collateral, asset, accounts, account):
    cog_pair = cog_low_pair

    asset.mint(account, 100 * 10 ** 18, sender=account)
    asset.approve(cog_pair, 100 * 10 ** 18, sender=account)
    cog_pair.deposit(100 * 10 ** 18, account, sender=account)

    account = accounts[1]

    collateral.mint(account, 1000 * 10 ** 18, sender=account)
    collateral.approve(cog_pair, 1000 * 10 ** 18, sender=account)
    cog_pair.add_collateral(account, 1000 * 10 ** 18, sender=account)

    (interest_per_second, last_accrued, fees_earned_fraction) = cog_pair.accrue_info()
    assert interest_per_second == ONE_PERCENT * 5
    cog_pair.borrow(1 * 10 ** 18, sender=account)

    boa.env.time_travel(86400 * 365)
    cog_pair.accrue(sender=account)

    (interest_per_second, last_accrued, fees_earned_fraction) = cog_pair.accrue_info()
    assert interest_per_second == ONE_PERCENT * 2
    cog_pair.borrow( 99 * 10 ** 18, sender=account)
    
    # Note to self, elasticity is low as shit so this should really be fixed
    boa.env.time_travel(86400 * 365 * 7)
    cog_pair.accrue(sender=account)
    (interest_per_second, last_accrued, fees_earned_fraction) = cog_pair.accrue_info()
    
    assert interest_per_second == ONE_PERCENT * 35

def test_interest_rate_maximum(cog_pair, collateral, asset, accounts, account):
    asset.mint(account, 100 * 10 ** 18, sender=account)
    asset.approve(cog_pair, 100 * 10 ** 18, sender=account)
    cog_pair.deposit(100 * 10 ** 18, account, sender=account)

    account = accounts[1]

    collateral.mint(account, 1000 * 10 ** 18, sender=account)
    collateral.approve(cog_pair, 1000 * 10 ** 18, sender=account)
    cog_pair.add_collateral(account, 1000 * 10 ** 18, sender=account)

    (interest_per_second, last_accrued, fees_earned_fraction) = cog_pair.accrue_info()
    assert interest_per_second == ONE_PERCENT * 7 
    cog_pair.borrow(1 * 10 ** 18, sender=account)

    boa.env.time_travel(86400 * 365)
    cog_pair.accrue(sender=account)

    (interest_per_second, last_accrued, fees_earned_fraction) = cog_pair.accrue_info()
    assert interest_per_second == ONE_PERCENT * 4
    cog_pair.borrow( 99 * 10 ** 18, sender=account)
    
    # Note to self, elasticity is low as shit so this should really be fixed
    boa.env.time_travel(86400 * 365 * 14)
    cog_pair.accrue(sender=account)
    (interest_per_second, last_accrued, fees_earned_fraction) = cog_pair.accrue_info()
    
    assert interest_per_second == ONE_PERCENT * 150


def test_high_interest_rate_maximum(cog_high_pair, collateral, asset, accounts, account):
    cog_pair = cog_high_pair

    asset.mint(account, 100 * 10 ** 18, sender=account)
    asset.approve(cog_pair, 100 * 10 ** 18, sender=account)
    cog_pair.deposit(100 * 10 ** 18, account, sender=account)

    account = accounts[1]

    collateral.mint(account, 1000 * 10 ** 18, sender=account)
    collateral.approve(cog_pair, 1000 * 10 ** 18, sender=account)
    cog_pair.add_collateral(account, 1000 * 10 ** 18, sender=account)

    (interest_per_second, last_accrued, fees_earned_fraction) = cog_pair.accrue_info()
    assert interest_per_second == ONE_PERCENT * 12
    cog_pair.borrow(1 * 10 ** 18, sender=account)

    boa.env.time_travel(86400 * 365)
    cog_pair.accrue(sender=account)

    (interest_per_second, last_accrued, fees_earned_fraction) = cog_pair.accrue_info()
    assert interest_per_second == ONE_PERCENT * 5
    cog_pair.borrow( 99 * 10 ** 18, sender=account)
    
    # Note to self, elasticity is low as shit so this should really be fixed
    boa.env.time_travel(86400 * 365 * 14)
    cog_pair.accrue(sender=account)
    (interest_per_second, last_accrued, fees_earned_fraction) = cog_pair.accrue_info()
    
    assert interest_per_second == ONE_PERCENT * 1000
