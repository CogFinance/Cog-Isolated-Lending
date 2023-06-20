import boa
import pytest

from datetime import timedelta

from hypothesis import (
    given,
    settings,
    strategies as st,
)

from tests.fixtures import *


def test_repay_invariants(cog_pair, oracle, accounts, collateral, asset):
    amount = 10000 * 10 ** 18
    # Initial setup
    account = accounts[0]
    asset_one_coin_price = 1000000000000000000

    oracle.setPrice(asset_one_coin_price, sender=account)
    oracle.setUpdated(True, sender=account)
    cog_pair.get_exchange_rate(sender=account)

    asset.mint(account, amount, sender=account)
    asset.approve(cog_pair, amount, sender=account)
    cog_pair.deposit(amount, account, sender=account)

    # Borrow
    account = accounts[1]
    collateral.mint(account, amount*10, sender=account)
    collateral.approve(cog_pair, amount*10, sender=account)
    cog_pair.add_collateral(account, amount*10, sender=account)

    cog_pair.borrow(account, amount, sender=account)

    # Repay
    (elastic, old_base) = cog_pair.total_borrow()
    old_borrow_part = cog_pair.user_borrow_part(account)

    # REPAY_BORROW_FEE and REPAY_BORROW_FEE_PRECISION both respectively
    fee = int((amount * 50) / 100000)

    asset.mint(account, amount+fee, sender=account)
    asset.approve(cog_pair, amount+fee, sender=account)
    cog_pair.repay(account, amount+fee, sender=account)

    (new_elastic, new_base) = cog_pair.total_borrow()
    new_borrow_part = cog_pair.user_borrow_part(account)

    assert new_base == old_base - amount - fee
    assert new_borrow_part == old_borrow_part - amount - fee

    # Test Can't overpay with repay
    asset.mint(account, amount*100, sender=account)
    asset.approve(cog_pair, amount*100, sender=account)

    with boa.reverts():
        cog_pair.repay(account, amount*100, sender=account)
