import boa
import pytest

from datetime import timedelta

from hypothesis import (
    given,
    settings,
    strategies as st,
)


def test_crv_pair_collateral(cog_high_pair, asset, oracle, collateral, accounts):
    crv_price_feed =  56000000
    weth_price_feed = 210000000000
    decimals = 10 ** 18


    oracle.setPrice(int((1e36 * weth_price_feed) / crv_price_feed / decimals), sender=accounts[0])
    oracle.setUpdated(True, sender=accounts[0])

    cog_high_pair.get_exchange_rate(sender=accounts[0])

    # 1500 Mock ETH to deposit
    DEPOSIT_AMOUNT = 1500 * 10 ** 18
    asset.mint(accounts[1], DEPOSIT_AMOUNT, sender=accounts[1])
    asset.approve(cog_high_pair, DEPOSIT_AMOUNT, sender=accounts[1])
    cog_high_pair.deposit(DEPOSIT_AMOUNT, sender=accounts[1])

    # Add 1000 CRV as collateral
    COLLATERAL_AMOUNT = 1000 * 10 ** 18
    collateral.mint(accounts[2], COLLATERAL_AMOUNT, sender=accounts[2])
    collateral.approve(cog_high_pair, COLLATERAL_AMOUNT, sender=accounts[2])
    cog_high_pair.add_collateral(accounts[2], COLLATERAL_AMOUNT , sender=accounts[2])
   
    # At $0.57 CRV and $2100 ETH, 1000 CRV as collateral is worth 0.2714 ETH
    # So we should be able to borrow 0.18998, and a borrow of 0.2174 eth (80%) should fail

    with boa.reverts("Insufficient Collateral"):
        cog_high_pair.borrow(int(0.2174 * 10 ** 18), sender=accounts[2])
    
    cog_high_pair.borrow(int(0.18998 * 10 ** 18), sender=accounts[2])

def test_crv_pair_asset(cog_high_pair, asset, oracle, collateral, accounts):
    crv_price_feed =  56000000
    weth_price_feed = 210000000000
    decimals = 10 ** 18


    oracle.setPrice(int((1e36 * crv_price_feed) / weth_price_feed / decimals), sender=accounts[0])
    oracle.setUpdated(True, sender=accounts[0])

    cog_high_pair.get_exchange_rate(sender=accounts[0])

    # 50,000 Mock CRV to deposit
    DEPOSIT_AMOUNT = 50_000 * 10 ** 18
    asset.mint(accounts[1], DEPOSIT_AMOUNT, sender=accounts[1])
    asset.approve(cog_high_pair, DEPOSIT_AMOUNT, sender=accounts[1])
    cog_high_pair.deposit(DEPOSIT_AMOUNT, sender=accounts[1])

    # Add 1 ETH as collateral
    COLLATERAL_AMOUNT = 1 * 10 ** 18
    collateral.mint(accounts[2], COLLATERAL_AMOUNT, sender=accounts[2])
    collateral.approve(cog_high_pair, COLLATERAL_AMOUNT, sender=accounts[2])
    cog_high_pair.add_collateral(accounts[2], COLLATERAL_AMOUNT , sender=accounts[2])
   
    # At $0.57 CRV and $2100 ETH, 1 ETH as collateral is worth 3684 CRV
    # So we should be able to borrow 2576 CRV, and a borrow of 2947 CRV (80%) should fail

    with boa.reverts("Insufficient Collateral"):
        cog_high_pair.borrow(int(2947 * 10 ** 18), sender=accounts[2])
    
    cog_high_pair.borrow(int(2576 * 10 ** 18), sender=accounts[2])

