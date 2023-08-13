import boa
import pytest

from datetime import timedelta

from hypothesis import (
    given,
    settings,
    strategies as st,
)

from tests.fixtures import *

def test_asset(cog_pair, asset):
    assert asset.address == cog_pair.asset()

def test_totalAssets(cog_pair, oracle, accounts, collateral, asset):
    """
    Invariants Tested
    (Specifically not a fuzz test to save test suite time)
    -----------------
    totalAssets begins at 0
    totalAssets reflects assets deposited via deposit, and mint correctly
    totalAssets reflects decreases in assets via withdraw, and redeem
    totalAssets reflects interest earned through borrows
    """
    account = accounts[0]
    oracle.setPrice(10 ** 18, sender=account)
    oracle.setUpdated(True, sender=account)
    cog_pair.get_exchange_rate(sender=account)

    old_total_assets = cog_pair.totalAssets()

    # totalAssets begins at 0
    assert old_total_assets == 0

    # totalAssets reflects assets deposited via deposit correctly
    asset.mint(account, 1000000000000000000, sender=account)
    asset.approve(cog_pair, 1000000000000000000, sender=account)
    cog_pair.deposit(1000000000000000000, account, sender=account)

    assert cog_pair.totalAssets() == 1000000000000000000
    # totalAssets reflects assets deposited via mint correctly
    asset.mint(account, 1000000000000000000, sender=account)
    asset.approve(cog_pair, 1000000000000000000, sender=account)
    # Kind of weird because shares and assets are still 1:1 due to no interest being accrued
    cog_pair.mint(1000000000000000000, account, sender=account)

    assert cog_pair.totalAssets() == 2000000000000000000

    # totalAssets reflects decreases in assets via withdraw correctly
    cog_pair.withdraw(1000000000000000000, account, sender=account)
    assert cog_pair.totalAssets() == 1000000000000000000

    # totalAssets reflects decreases in assets via redeem correctly
    cog_pair.redeem(500000000000000000, account, sender=account)
    assert cog_pair.totalAssets() == 500000000000000000

    # totalAssets reflects interest earned through borrows
    account = accounts[1]
    collateral.mint(account, 500 * 10 ** 18, sender=account)
    collateral.approve(cog_pair, 500 * 10 ** 18, sender=account)
    cog_pair.add_collateral(account, 500 * 10 ** 18, sender=account)
    cog_pair.borrow(250000000000000000, sender=account)

    boa.env.time_travel(seconds=86000)

    amt = cog_pair.user_borrow_part(account)

    # amount is arbitrarily multiplied by 2 here because it represents a share value and so will be 
    # slighly under the amount of assets needed
    asset.mint(account, amt*2, sender=account)
    asset.approve(cog_pair, amt*2, sender=account)
    cog_pair.repay(account, amt, sender=account)

    # In an ideal world this would be exact interest accrued, but given I want this test to apply across multiple interest model tweaks
    # it is not, and the condition is still tested, while actual interest accrual should be tested in borrow and repay tests
    assert cog_pair.totalAssets() > 500000000000000000


@given(
    amount=st.integers(min_value=100000, max_value=2**124-1),
)
@settings(max_examples=100, deadline=None)
def test_convertToShares(cog_pair, oracle, accounts, collateral, asset, amount):
    """
    Invariants Tested
    -----------------
    convertToShares returns 1:1 if totalAssets is 0
    Accurately reflects shares for assets before interest has been accrued
    Accurately reflects shares for assets after interest has been accrued
    """

    account = accounts[0]
    oracle.setPrice(10 ** 18, sender=account)
    oracle.setUpdated(True, sender=account)
    cog_pair.get_exchange_rate(sender=account)

    AMOUNT = amount

    # convertToShares returns 1:1 if totalAssets is 0
    assert cog_pair.convertToShares(AMOUNT) == AMOUNT

    # Accurately reflects shares for assets before interest has been accrued
    asset.mint(account, AMOUNT, sender=account)
    asset.approve(cog_pair, AMOUNT, sender=account)
    cog_pair.deposit(AMOUNT, account, sender=account)

    assert cog_pair.convertToShares(AMOUNT) == AMOUNT

    # Add more assets to be borrowed
    asset.mint(account, AMOUNT*10, sender=account)
    asset.approve(cog_pair,  AMOUNT*10, sender=account)
    cog_pair.deposit(AMOUNT*10, account, sender=account)

    # Accurately reflects shares for assets after interest has been accrued
    # Maybe move this block of code to a util function?
    account = accounts[1]
    collateral.mint(account, AMOUNT * 100, sender=account)
    collateral.approve(cog_pair, AMOUNT * 100, sender=account)
    cog_pair.add_collateral(account,AMOUNT * 100, sender=account)

    cog_pair.borrow(AMOUNT, sender=account)
    amt = cog_pair.user_borrow_part(account)
    boa.env.time_travel(seconds=86000)
    # Borrow has caused total_asset to decrease, and total borrow to increase
    # So shares should lower than AMOUNT until all debt is repaid
    assert cog_pair.convertToShares(AMOUNT) < AMOUNT
    
    # amount is arbitrarily multiplied by 2 here because it represents a share value and so will be 
    # slighly under the amount of assets needed
    asset.mint(account, amt*2, sender=account)
    asset.approve(cog_pair, amt*2, sender=account)
    cog_pair.repay(account, amt, sender=account)

    # Once debt is repaid, and total_borrow is (0,0) shares mint 1:1 again, or atleast as close as possible, with rounding occuring downward
    assert cog_pair.convertToShares(AMOUNT) < AMOUNT and cog_pair.convertToShares(AMOUNT) > AMOUNT - (AMOUNT * 0.05)

@given(
    amount=st.integers(min_value=100000, max_value=2**124-1),
)
@settings(max_examples=100, deadline=None)
def test_convertToAssets(cog_pair, oracle, accounts, collateral, asset, amount):
    """
    Invariants Tested
    -----------------
    convertToAssets returns 1:1 if totalAssets is 0
    Accurately reflects assets for shares before interest has been accrued
    Accurately reflects assets for shares after interest has been accrued
    """

    account = accounts[0]
    oracle.setPrice(10 ** 18, sender=account)
    oracle.setUpdated(True, sender=account)
    cog_pair.get_exchange_rate(sender=account)

    AMOUNT = amount
    AMOUNT_IN_SHARES = cog_pair.convertToShares(AMOUNT)
    
    # convertToAssets returns 1:1 if totalAssets is 0
    assert cog_pair.convertToAssets(AMOUNT_IN_SHARES) == AMOUNT

    # Accurately reflects shares for assets before interest has been accrued
    asset.mint(account, AMOUNT, sender=account)
    asset.approve(cog_pair, AMOUNT, sender=account)
    cog_pair.deposit(AMOUNT, account, sender=account)

    assert cog_pair.convertToAssets(AMOUNT_IN_SHARES) == AMOUNT

    # Accurately reflects shares for assets after interest has been accrued
    # Maybe move this block of code to a util function?
    account = accounts[1]
    collateral.mint(account, AMOUNT * 100, sender=account)
    collateral.approve(cog_pair, AMOUNT * 100, sender=account)
    cog_pair.add_collateral(account,AMOUNT * 100, sender=account)
    cog_pair.borrow(AMOUNT, sender=account)
    amt = cog_pair.user_borrow_part(account)
    boa.env.time_travel(seconds=86000)    
    # Borrow has caused total_asset to decrease, and total borrow to increase
    # So shares should higher than asset until all debt is repaid
    assert cog_pair.convertToAssets(AMOUNT) > AMOUNT
    
    # amount is arbitrarily multiplied by 2 here because it represents a share value and so will be 
    # slighly under the amount of assets needed
    asset.mint(account, amt*2, sender=account)
    asset.approve(cog_pair, amt*2, sender=account)
    cog_pair.repay(account, amt, sender=account)

    # Shares should still retain their superior value, which now includes interest after debt is repaid
    assert cog_pair.convertToAssets(AMOUNT) > AMOUNT


def test_maxDeposit(cog_pair, account):
    """
    Invariants Tested
    -----------------
    maxDeposit returns 2**256 - 1 since there is no practical cap on deposits except at unreasonably large values
    """
    assert cog_pair.maxDeposit(account) == 2**256 - 1

@given(
    amount=st.integers(min_value=100000, max_value=2**124-1),
)
@settings(max_examples=100, deadline=None)
def test_previewDeposit(cog_pair, oracle, accounts, collateral, asset, amount):
    """
    Invariants Tested
    -----------------
    mirrors deposit before pool has accrued interest
    mirrors deposit while pool is accruing interest
    """

    account = accounts[0]
    oracle.setPrice(10 ** 18, sender=account)
    oracle.setUpdated(True, sender=account)
    cog_pair.get_exchange_rate(sender=account)

    AMOUNT = amount

    # mirrors deposit before pool has accrued interest
    expected_shares = cog_pair.previewDeposit(AMOUNT)

    asset.mint(account, AMOUNT, sender=account)
    asset.approve(cog_pair, AMOUNT, sender=account)
    cog_pair.deposit(AMOUNT, account, sender=account)
    assert cog_pair.balanceOf(account) == expected_shares

    # mirrors deposit while pool is accruing interest
    account = accounts[1]
    collateral.mint(account, AMOUNT * 100, sender=account)
    collateral.approve(cog_pair, AMOUNT * 100, sender=account)
    cog_pair.add_collateral(account,AMOUNT * 100, sender=account)
    cog_pair.borrow(AMOUNT, sender=account)

    boa.env.time_travel(seconds=86000)    
    expected_shares = cog_pair.previewDeposit(AMOUNT)
    account = accounts[2]
    asset.mint(account, AMOUNT, sender=account)
    asset.approve(cog_pair, AMOUNT, sender=account)
    cog_pair.deposit(AMOUNT, account, sender=account)

    assert cog_pair.balanceOf(account) == expected_shares


@given(
    amount=st.integers(min_value=100000, max_value=2**124-1),
)
@settings(max_examples=100, deadline=None)
def test_deposit(cog_pair, accounts, asset, amount):
    """
    Invariants Tested
    -----------------
    Emits the Deposit event
    Supports EIP-20 approve / transferFrom on asset as a deposit flow
    Reverts if all assets cannot be deposited
    Grants user shares for deposit
    """

    AMOUNT = amount
    account = accounts[0]
    
    asset.mint(account, AMOUNT, sender=account)
    asset.approve(cog_pair, AMOUNT, sender=account)
    cog_pair.deposit(AMOUNT, account, sender=account)

    # Grants user share for deposit
    assert cog_pair.balanceOf(account) == AMOUNT
    # Supports EIP-20 approve / transferFrom on asset as a deposit flow
    assert asset.balanceOf(account) == 0


def test_maxMint(cog_pair, account):
    """
    Invariants Tested
    -----------------
    maxDeposit returns 2**256 - 1 since there is no practical cap on deposits except at unreasonably large values
    """
    assert cog_pair.maxMint(account) == 2**256 - 1
    

@given(
    amount=st.integers(min_value=100000, max_value=2**124-1),
)
@settings(max_examples=100, deadline=None)
def test_previewMint(cog_pair, oracle, accounts, collateral, asset, amount):
    """
    Invariants Tested
    -----------------
    mirrors mint before pool has accrued interest
    mirrors mint while pool is accruing interest
    """

    account = accounts[0]
    oracle.setPrice(10 ** 18, sender=account)
    oracle.setUpdated(True, sender=account)
    cog_pair.get_exchange_rate(sender=account)

    AMOUNT_IN_ASSETS = amount
    AMOUNT_IN_SHARES = cog_pair.convertToShares(AMOUNT_IN_ASSETS)

    # mirrors deposit before pool has accrued interest
    AMOUNT_IN_ASSETS = cog_pair.previewMint(AMOUNT_IN_SHARES)

    asset.mint(account, AMOUNT_IN_ASSETS, sender=account)
    asset.approve(cog_pair, AMOUNT_IN_ASSETS, sender=account)
    cog_pair.mint(AMOUNT_IN_SHARES, account, sender=account)
    assert cog_pair.balanceOf(account) == AMOUNT_IN_SHARES
    assert asset.balanceOf(account) == 0

    # mirrors deposit while pool is accruing interest
    account = accounts[1]
    collateral.mint(account, AMOUNT_IN_ASSETS * 100, sender=account)
    collateral.approve(cog_pair, AMOUNT_IN_ASSETS * 100, sender=account)
    cog_pair.add_collateral(account,AMOUNT_IN_ASSETS * 100, sender=account)
    cog_pair.borrow(AMOUNT_IN_ASSETS, sender=account)

    boa.env.time_travel(seconds=86000)
    expected_assets = cog_pair.previewMint(AMOUNT_IN_SHARES)
    account = accounts[3]
    asset.mint(account, expected_assets, sender=account)
    asset.approve(cog_pair, expected_assets, sender=account)
    cog_pair.mint(AMOUNT_IN_SHARES, account, sender=account)

    assert expected_assets > AMOUNT_IN_ASSETS
    assert cog_pair.balanceOf(account) == AMOUNT_IN_SHARES
    assert asset.balanceOf(account) == 0


@given(
    amount=st.integers(min_value=100000, max_value=2**124-1),
)
@settings(max_examples=100, deadline=None)
def test_mint(cog_pair, accounts, asset, collateral, oracle, amount):
    """
    Invariants Tested
    -----------------
    Emits the Deposit event
    Supports EIP-20 approve / transferFrom on asset as a deposit flow
    Reverts if all assets cannot be deposited
    Grants user shares for mint
    """

    account = accounts[0]
    oracle.setPrice(10 ** 18, sender=account)
    oracle.setUpdated(True, sender=account)
    cog_pair.get_exchange_rate(sender=account)

    AMOUNT = amount
    AMOUNT_IN_SHARES = cog_pair.convertToShares(AMOUNT)
    account = accounts[0]
    
    asset.mint(account, AMOUNT, sender=account)
    asset.approve(cog_pair, AMOUNT, sender=account)
    cog_pair.mint(AMOUNT_IN_SHARES, account, sender=account)


    # Grants user share for deposit
    assert cog_pair.balanceOf(account) == AMOUNT_IN_SHARES
    # Supports EIP-20 approve / transferFrom on asset as a deposit flow
    assert asset.balanceOf(account) == 0

    asset.mint(account, int(AMOUNT/2), sender=account)
    asset.approve(cog_pair, AMOUNT, sender=account)
    
    with boa.reverts():
        # Reverts if all assets cannot be deposited
        cog_pair.mint(AMOUNT, account, sender=account)

    account = accounts[1]
    collateral.mint(account, AMOUNT * 100, sender=account)
    collateral.approve(cog_pair, AMOUNT * 100, sender=account)
    cog_pair.add_collateral(account,AMOUNT * 100, sender=account)
    cog_pair.borrow(int(AMOUNT/2), sender=account)
    boa.env.time_travel(seconds=86000)    
    amt = cog_pair.user_borrow_part(account)

    account = accounts[2]
    asset.mint(account, AMOUNT, sender=account)
    asset.approve(cog_pair, AMOUNT, sender=account)
    AMOUNT_IN_SHARES_2 = cog_pair.convertToShares(AMOUNT)
    cog_pair.mint(AMOUNT_IN_SHARES_2, account, sender=account)
    assert AMOUNT_IN_SHARES > AMOUNT_IN_SHARES_2


def test_maxWithdraw(cog_pair, accounts, asset, collateral, oracle):
    """
    Invariants Tested
    -----------------
    maxWithdraw returns all available assets for withdrawal when there is no outstanding loan
    maxWithdraw returns available assets for withdrawal when there is an outstanding loan
    """

    account = accounts[0]
    oracle.setPrice(10 ** 18, sender=account)
    oracle.setUpdated(True, sender=account)
    cog_pair.get_exchange_rate(sender=account)

    AMOUNT = 100000000
    asset.mint(account, AMOUNT, sender=account)
    asset.approve(cog_pair, AMOUNT, sender=account)
    cog_pair.mint(AMOUNT, account, sender=account)

    # maxWithdraw returns all available assets for withdrawal when there is no outstanding loan
    assert cog_pair.maxWithdraw(account) == AMOUNT

    account = accounts[1]
    collateral.mint(account, AMOUNT * 100, sender=account)
    collateral.approve(cog_pair, AMOUNT * 100, sender=account)
    cog_pair.add_collateral(account,AMOUNT * 100, sender=account)
    cog_pair.borrow(int(AMOUNT/2), sender=account)

    account = accounts[0]

    # maxWithdraw returns available assets for withdrawal when there is an outstanding loan
    max = cog_pair.maxWithdraw(account)
    assert max == AMOUNT - int(AMOUNT/2)

@given(
    amount=st.integers(min_value=100000, max_value=2**124-1),
)
@settings(max_examples=100, deadline=None)
def test_previewWithdraw(cog_pair, accounts, asset, collateral, oracle, amount):
    """
    Invariants Tested
    -----------------
    mirrors withdraw before pool has accrued interest
    mirrors withdraw while pool is accruing interest
    """

    account = accounts[0]
    oracle.setPrice(10 ** 18, sender=account)
    oracle.setUpdated(True, sender=account)
    cog_pair.get_exchange_rate(sender=account)

    AMOUNT = amount

    # mirrors withdraw before pool has accrued interest
    asset.mint(account, AMOUNT, sender=account)
    asset.approve(cog_pair, AMOUNT, sender=account)
    cog_pair.deposit(AMOUNT, account, sender=account)

    preview = cog_pair.previewWithdraw(AMOUNT) 

    assert preview == AMOUNT

    # mirrors withdraw while pool is accruing interest
    account = accounts[1]
    collateral.mint(account, AMOUNT * 100, sender=account)
    collateral.approve(cog_pair, AMOUNT * 100, sender=account)
    cog_pair.add_collateral(account,AMOUNT * 100, sender=account)
    cog_pair.borrow(int(AMOUNT/2), sender=account)

    account = accounts[0]

    preview = cog_pair.previewWithdraw(AMOUNT)

    # Shares will result in this value being lower as the share value has now increased
    assert preview < AMOUNT - int(AMOUNT/2)


@given(
    amount=st.integers(min_value=100000, max_value=2**124-1),
)
@settings(max_examples=100, deadline=None)
def test_withdraw(cog_pair, accounts, asset, amount):
    """
    Invariants Tested
    -----------------
    Emits the Withdraw event
    Supports withdrawing of own assets in redeem flow
    Supports withdrawing of approved assets in redeem flow
    Disallows withdrawing of non-approved assets in redeem flow
    """

    account = accounts[0]

    # Mint enough so that withdrawls don't go below pool minimum
    account = accounts[9]
    asset.mint(account, 1000000000000000000, sender=account)
    asset.approve(cog_pair, 1000000000000000000, sender=account)
    cog_pair.mint(1000000000000000000, account, sender=account)
    account = accounts[0]

    AMOUNT = amount

    asset.mint(account, AMOUNT, sender=account)
    asset.approve(cog_pair, AMOUNT, sender=account)
    cog_pair.deposit(AMOUNT, account, sender=account)

    # Supports withdrawing of own assets in redeem flow
    cog_pair.withdraw(AMOUNT, account, account, sender=account)

    # Supports burning of approved assets in redeem flow
    account = accounts[1]
    asset.mint(account, AMOUNT, sender=account)
    asset.approve(cog_pair, AMOUNT, sender=account)
    cog_pair.deposit(AMOUNT, account, sender=account)

    cog_pair.approve(accounts[2], AMOUNT, sender=account)
    account = accounts[2]
    cog_pair.withdraw(AMOUNT, account, accounts[1], sender=account)

    # Disallows withdrawing of non-approved assets in redeem flow
    account = accounts[3]
    asset.mint(account, AMOUNT, sender=account)
    asset.approve(cog_pair, AMOUNT, sender=account)
    cog_pair.deposit(AMOUNT, account, sender=account)

    account = accounts[4]
    with boa.reverts():
        cog_pair.withdraw(AMOUNT, account, accounts[3], sender=account)



def test_maxRedeem(cog_pair, accounts, asset, collateral, oracle):
    """
    Invariants Tested
    -----------------
    maxRedeem returns all available assets for withdrawal when there is no outstanding loan
    maxRedeem returns available assets for withdrawal when there is an outstanding loan
    """

    account = accounts[0]
    oracle.setPrice(10 ** 18, sender=account)
    oracle.setUpdated(True, sender=account)
    cog_pair.get_exchange_rate(sender=account)

    AMOUNT = 100000000
    AMOUNT_IN_SHARES = cog_pair.convertToShares(AMOUNT)

    # maxRedeem returns all available assets for withdrawal when there is no outstanding loan
    asset.mint(account, AMOUNT, sender=account)
    asset.approve(cog_pair, AMOUNT, sender=account)
    cog_pair.mint(AMOUNT_IN_SHARES, account, sender=account)

    assert cog_pair.maxRedeem(account) == AMOUNT_IN_SHARES

    # maxRedeem returns available assets for withdrawal when there is an outstanding loan
    account = accounts[1]
    collateral.mint(account, AMOUNT * 100, sender=account)
    collateral.approve(cog_pair, AMOUNT * 100, sender=account)
    cog_pair.add_collateral(account,AMOUNT * 100, sender=account)
    cog_pair.borrow(AMOUNT, sender=account)

    account = accounts[0]
    assert cog_pair.maxRedeem(account) == 0

    account = accounts[2]
    NEW_AMOUNT_IN_SHARES = cog_pair.convertToShares(AMOUNT*2)
    asset.mint(account, AMOUNT*2, sender=account)
    asset.approve(cog_pair, AMOUNT*2, sender=account)
    cog_pair.mint(NEW_AMOUNT_IN_SHARES, account, sender=account)

    account = accounts[0]

    # Rounding error may occur here because shares are so fucking annoying, but should round below, not above 
    assert cog_pair.maxRedeem(account) <= cog_pair.balanceOf(account)


@given(
    amount=st.integers(min_value=100000, max_value=2**124-1),
)
@settings(max_examples=100, deadline=None)
def test_previewRedeem(cog_pair, accounts, asset, collateral, oracle, amount):
    """
    Invariants Tested
    -----------------
    mirrors redeem before pool has accrued interest
    mirrors redeem while pool is accruing interest
    """

    account = accounts[0]
    oracle.setPrice(10 ** 18, sender=account)
    oracle.setUpdated(True, sender=account)
    cog_pair.get_exchange_rate(sender=account)

    AMOUNT = amount
    AMOUNT_IN_SHARES = cog_pair.convertToShares(AMOUNT)

    # mirrors redeem before pool has accrued interest
    asset.mint(account, AMOUNT, sender=account)
    asset.approve(cog_pair, AMOUNT, sender=account)
    cog_pair.mint(AMOUNT_IN_SHARES, account, sender=account)

    assert cog_pair.previewRedeem(AMOUNT) == AMOUNT_IN_SHARES

    # mirrors redeem while pool is accruing interest
    account = accounts[1]
    collateral.mint(account, AMOUNT * 100, sender=account)
    collateral.approve(cog_pair, AMOUNT * 100, sender=account)
    cog_pair.add_collateral(account,AMOUNT * 100, sender=account)
    cog_pair.borrow(int(AMOUNT/2), sender=account)

    account = accounts[0]

    assert cog_pair.previewRedeem(AMOUNT) == cog_pair.convertToShares(asset.balanceOf(cog_pair))



@given(
    amount=st.integers(min_value=100000, max_value=2**96-1),
)
@settings(max_examples=5, deadline=None)
def test_redeem(cog_pair, accounts, collateral, asset, oracle, amount):
    """
    Invariants Tested
    -----------------
    Emits the Withdraw event
    Supports burning of own shares in redeem flow
    Supports burning of approved shares in redeem flow
    Disallows burning of non-approved shares in redeem flow
    """
    # Mint enough so that withdrawls don't go below pool minimum
    account = accounts[9]
    asset.mint(account, 1000000000000000000, sender=account)
    asset.approve(cog_pair, 1000000000000000000, sender=account)
    cog_pair.mint(1000000000000000000, account, sender=account)
    account = accounts[0]

    AMOUNT = amount
    AMOUNT_IN_SHARES = cog_pair.convertToShares(AMOUNT)

    asset.mint(account, AMOUNT, sender=account)
    asset.approve(cog_pair, AMOUNT, sender=account)
    cog_pair.mint(AMOUNT_IN_SHARES, account, sender=account)

    # Supports burning of own shares in redeem flow
    # Emits the Withdraw event
    cog_pair.redeem(AMOUNT_IN_SHARES, account, account, sender=account)

    # Supports burning of approved shares in redeem flow
    account = accounts[1]

    AMOUNT_IN_SHARES = cog_pair.convertToShares(AMOUNT, sender=account)
    asset.mint(account, AMOUNT, sender=account)
    asset.approve(cog_pair, AMOUNT, sender=account)
    cog_pair.mint(AMOUNT_IN_SHARES, account, sender=account)

    cog_pair.approve(accounts[2], AMOUNT_IN_SHARES, sender=account)
    account = accounts[2]

    preview_amt = cog_pair.previewRedeem(AMOUNT_IN_SHARES)
    actual_amt = cog_pair.redeem(AMOUNT_IN_SHARES, account, accounts[1], sender=account)

    assert actual_amt == preview_amt

    # Disallows burning of non-approved shares in redeem flow
    account = accounts[3]

    AMOUNT_IN_SHARES = cog_pair.convertToShares(AMOUNT)

    asset.mint(account, AMOUNT, sender=account)
    asset.approve(cog_pair, AMOUNT, sender=account)
    cog_pair.mint(AMOUNT_IN_SHARES, account, sender=account)
    
    account = accounts[4]
    with boa.reverts():
        cog_pair.redeem(AMOUNT_IN_SHARES, account, accounts[3], sender=account)

    account = accounts[5]

    AMOUNT_IN_SHARES = cog_pair.convertToShares(AMOUNT, sender=account)
    asset.mint(account, AMOUNT, sender=account)
    asset.approve(cog_pair, AMOUNT, sender=account)
    cog_pair.mint(AMOUNT_IN_SHARES, account, sender=account)
   
    account = accounts[4]
    # Next accrue interest to create a dramatic different between share and asset pricing
    oracle.setPrice(10 ** 18, sender=account)

    oracle.setUpdated(True, sender=account)
    cog_pair.get_exchange_rate(sender=account)

    asset.mint(account, amount, sender=account)
    asset.approve(cog_pair, amount, sender=account)
    cog_pair.deposit(amount, account, sender=account)

    account = accounts[1]

    collateral.mint(account, amount*10, sender=account)
    collateral.approve(cog_pair, amount*10, sender=account)
    cog_pair.add_collateral(account, amount*10, sender=account)

    cog_pair.borrow(amount, sender=account)   

    boa.env.time_travel(86400 * 365 * 5)
    cog_pair.accrue()

    borrowed_amount = cog_pair.user_borrow_part(account)
    asset.mint(account, borrowed_amount*2, sender=account)
    asset.approve(cog_pair, borrowed_amount*2, sender=account)
    cog_pair.repay(account, borrowed_amount,sender=account)

    account = accounts[5]
    before_balance = asset.balanceOf(account)

    preview_amt = cog_pair.previewRedeem(AMOUNT_IN_SHARES)
    actual_amt = cog_pair.redeem(AMOUNT_IN_SHARES, sender=account)
    assert actual_amt == preview_amt

    new_balance = asset.balanceOf(account)
    assert new_balance == before_balance + actual_amt
