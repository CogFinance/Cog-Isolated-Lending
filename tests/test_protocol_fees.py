import ape
import pytest
from hypothesis import (
    given,
    settings,
    strategies as st,
)

from tests.fixtures import *

def test_borrow_fee_accumulates(chain, accounts, collateral, asset, oracle, cog_pair):
    snap = chain.snapshot()
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

    cog_pair.borrow(account, AMOUNT // 2, sender=account)

    accrue_info = cog_pair.accrue_info()
    
    fees = accrue_info.fees_earned_fraction

    assert fees == 0

    accrue_info = cog_pair.accrue_info()

    last_accrued = accrue_info.last_accrued

    # Ensure borrow fee accrues
    # 0.05% borrow opening fee
    interest_accrued = (
        cog_pair.total_borrow().elastic
        * cog_pair.accrue_info().interest_per_second
        * (chain.pending_timestamp - last_accrued)
        / 1000000000000000000
    )

    expected_fee = (interest_accrued * cog_pair.protocol_fee()) / 1000000

    cog_pair.accrue(sender=account)
    accrue_info = cog_pair.accrue_info()

    fees = accrue_info.fees_earned_fraction

    # Account for 5% error due to inconsistencies in timestamps
    assert fees >= (expected_fee * 95) / 100 and fees <= (expected_fee * 105) / 100

    chain.restore(snap)

def test_surge_fee_enacts(chain, accounts, collateral, asset, oracle, cog_pair):
    snap = chain.snapshot()
    account = accounts[0]
    oracle.setPrice(5000000000000000000, sender=account)
    oracle.setUpdated(True, sender=account)
    cog_pair.get_exchange_rate(sender=account)

    AMOUNT = 10 * 10 ** 18

    # Fill the pool with some assets
    asset.mint(account, AMOUNT, sender=account)
    asset.approve(cog_pair, AMOUNT, sender=account)
    cog_pair.deposit(AMOUNT, account, sender=account)

    # Borrow some assets
    account = accounts[1]
    collateral.mint(account, AMOUNT*100, sender=account)
    collateral.approve(cog_pair, AMOUNT*100, sender=account)
    cog_pair.add_collateral(account, AMOUNT*100, sender=account)

    cog_pair.accrue(sender=account)

    cog_pair.borrow(account, (AMOUNT // 60), sender=account)

    # Protocol fee is at 100% during surge
    assert cog_pair.protocol_fee() == 1000000

    chain.restore(snap)

