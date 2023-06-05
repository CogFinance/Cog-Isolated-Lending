import ape
import pytest
from hypothesis import (
    given,
    settings,
    strategies as st,
)

from tests.fixtures import *


def test_cannot_liquidate(cog_pair, accounts, chain, collateral, asset, oracle):
    snap = chain.snapshot()
    account = accounts[0]
    oracle.setPrice(5000000000000000000, sender=account)
    oracle.setUpdated(True, sender=account)
    cog_pair.get_exchange_rate(sender=account)

    assert cog_pair.exchange_rate() == 5000000000000000000

    account = accounts[1]

    asset.mint(account, 90000000000000000000000000000, sender=account)
    asset.approve(cog_pair, 90000000000000000000000000000, sender=account)
    cog_pair.deposit(90000000000000000000000000000, account, sender=account)

    account = accounts[2]
    collateral.mint(account, 90000000000000000000000000000, sender=account)
    collateral.approve(cog_pair, 90000000000000000000000000000, sender=account)
    cog_pair.add_collateral(account, 90000000000000000000000000000, sender=account)

    cog_pair.borrow(account, 1340000000000000000000000000, sender=account)

    assert asset.balanceOf(account) == 1340000000000000000000000000

    cog_pair.accrue(sender=account)

    account = accounts[1]

    asset.mint(account, 90000000000000000000000000000, sender=account)
    asset.approve(cog_pair, 90000000000000000000000000000, sender=account)
    
    with ape.reverts():
        cog_pair.liquidate(
            account,
            157563025210084033613445378,
            accounts[2],
            sender=account
        )

    chain.restore(snap)

def test_can_liquidate(cog_pair, accounts, chain, collateral, asset, oracle):
    account = accounts[0]
    oracle.setPrice(5000000000000000000, sender=account)
    oracle.setUpdated(True, sender=account)
    cog_pair.get_exchange_rate(sender=account)

    assert cog_pair.exchange_rate() == 5000000000000000000

    account = accounts[1]

    asset.mint(account, 90000000000000000000000000000, sender=account)
    asset.approve(cog_pair, 90000000000000000000000000000, sender=account)
    cog_pair.deposit(90000000000000000000000000000, account, sender=account)

    account = accounts[2]

    collateral.mint(account, 90000000000000000000000000000, sender=account)
    collateral.approve(cog_pair, 90000000000000000000000000000, sender=account)
    cog_pair.add_collateral(account, 90000000000000000000000000000, sender=account)

    cog_pair.borrow(account, 1340000000000000000000000000, sender=account)

    assert asset.balanceOf(account) == 1340000000000000000000000000

    oracle.setPrice(510000000000000000000, sender=account)
    oracle.setUpdated(True, sender=account)
    cog_pair.get_exchange_rate(sender=account)

    cog_pair.accrue(sender=account)

    account = accounts[1]

    asset.mint(account, 90000000000000000000000000000, sender=account)
    asset.approve(cog_pair, 90000000000000000000000000000, sender=account)

    cog_pair.liquidate(
        accounts[2],
        157563024000000000000000000,
        accounts[1],
        sender=accounts[1]
    )