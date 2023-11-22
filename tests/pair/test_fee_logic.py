import boa
import pytest
from hypothesis import (
    given,
    settings,
    strategies as st,
)

def test_borrow_fee_accumulates(accounts, collateral, asset, oracle, cog_pair):
    account = accounts[0]
    oracle.setPrice(10 ** 18, sender=account)
    oracle.setUpdated(True, sender=account)
    cog_pair.get_exchange_rate(sender=account)

    AMOUNT = 10 * 10 ** 18

    # Fill the pool with some assets
    asset.mint(account, AMOUNT, sender=account)
    asset.approve(cog_pair, AMOUNT, sender=account)
    cog_pair.deposit(AMOUNT, account, sender=account)

    # Borrow some assets
    account = accounts[1]
    collateral.mint(account, AMOUNT, sender=account)
    collateral.approve(cog_pair, AMOUNT, sender=account)
    cog_pair.add_collateral(account, AMOUNT, sender=account)

    cog_pair.accrue(sender=account)

    cog_pair.borrow(AMOUNT // 2, sender=account)

    (interest_per_second, last_accrued, fees_earned_fraction) = cog_pair.accrue_info()
    
    fees = fees_earned_fraction

    assert fees == 0

    (interest_per_second, last_accrued, fees_earned_fraction) = cog_pair.accrue_info()


    (elastic, base) = cog_pair.total_borrow()
    # Ensure borrow fee accrues
    # 0.05% borrow opening fee
    interest_accrued = (
        elastic
        * interest_per_second
        * (boa.env.vm.state.timestamp - last_accrued)
        / 1000000000000000000
    )

    expected_fee = (interest_accrued * cog_pair.protocol_fee()) / 1000000

    cog_pair.accrue(sender=account)
    accrue_info = cog_pair.accrue_info()

    (_, _, fees_earned_fraction) = cog_pair.accrue_info()

    # Account for 5% error due to inconsistencies in timestamps
    assert fees >= (expected_fee * 95) / 100 and fees <= (expected_fee * 105) / 100

def test_surge_fee_enacts(accounts, collateral, asset, oracle, cog_pair):
    admin = accounts[0]
    test_user = accounts[1]

    AMOUNT = 10 * 10 ** 18

    with boa.env.prank(admin):
        oracle.setPrice(5000000000000000000)
        oracle.setUpdated(True)
        cog_pair.get_exchange_rate()

        # Fill the pool with some assets
        asset.mint(admin, AMOUNT)
        asset.approve(cog_pair, AMOUNT)
        cog_pair.deposit(AMOUNT, admin)

    # Borrow some assets
    with boa.env.prank(test_user):
        collateral.mint(test_user, AMOUNT*100)
        collateral.approve(cog_pair, AMOUNT*100)
        cog_pair.add_collateral(test_user, AMOUNT*100)

        cog_pair.accrue()

        cog_pair.borrow(AMOUNT)

    boa.env.time_travel(86400 * 25)
    cog_pair.accrue()

    # Protocol fee is at 100% during surge
    assert cog_pair.protocol_fee() == 1000000

    boa.env.time_travel(86400 * 3)

    cog_pair.accrue()

    # Interest rate continues to grow by enough to trip the surge, so it doesn't end
    assert cog_pair.protocol_fee() == 1000000

    with boa.env.prank(test_user):
        asset.mint(test_user, AMOUNT*100)
        asset.approve(cog_pair, AMOUNT*100)

        # Repay under half of the loan
        cog_pair.repay(test_user, AMOUNT)

    # Interest rate will now decrease
    boa.env.time_travel(86400 * 5)
    cog_pair.accrue()

    assert cog_pair.protocol_fee() == 100000

def test_roll_over_pol(accounts, collateral, asset, oracle, cog_pair):
    account = accounts[3]
    oracle.setPrice(10 ** 18, sender=account)
    oracle.setUpdated(True, sender=account)
    cog_pair.get_exchange_rate(sender=account)

    AMOUNT = 10 * 10 ** 18

    # Fill the pool with some assets
    asset.mint(account, AMOUNT, sender=account)
    asset.approve(cog_pair, AMOUNT, sender=account)
    cog_pair.deposit(AMOUNT, account, sender=account)

    # Borrow some assets
    account = accounts[1]
    collateral.mint(account, AMOUNT, sender=account)
    collateral.approve(cog_pair, AMOUNT, sender=account)
    cog_pair.add_collateral(account, AMOUNT, sender=account)

    cog_pair.accrue(sender=account)

    cog_pair.borrow(AMOUNT // 2, sender=account)

    (interest_per_second, last_accrued, fees_earned_fraction) = cog_pair.accrue_info()
    
    fees = fees_earned_fraction

    assert fees == 0

    (interest_per_second, last_accrued, fees_earned_fraction) = cog_pair.accrue_info()


    (elastic, base) = cog_pair.total_borrow()
    # Ensure borrow fee accrues
    # 0.05% borrow opening fee
    interest_accrued = (
        elastic
        * interest_per_second
        * (boa.env.vm.state.timestamp - last_accrued)
        / 1000000000000000000
    )

    expected_fee = (interest_accrued * cog_pair.protocol_fee()) / 1000000

    cog_pair.accrue(sender=account)
    (_, _, fees_earned_fraction) = cog_pair.accrue_info()

    # Account for 5% error due to inconsistencies in timestamps
    assert fees >= (expected_fee * 95) / 100 and fees <= (expected_fee * 105) / 100

    cog_pair.roll_over_pol(sender=account)

    assert cog_pair.balanceOf(accounts[0]) == fees

    (_, _, fees_earned_fraction) = cog_pair.accrue_info()

    assert fees_earned_fraction == 0
