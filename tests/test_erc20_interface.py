import ape
import pytest

from datetime import timedelta

from hypothesis import (
    given,
    settings,
    strategies as st,
)

from tests.fixtures import (
    account,
    collateral,
    asset,
    oracle,
    cog_pair_blueprint,
    cog_factory,
    cog_pair
)

# Invariants found from https://eips.ethereum.org/EIPS/eip-20

def test_totalSupply(cog_pair, accounts, asset):
    """
    Invariants Tested
    -----------------
    1. `totalSupply` is set equal to 0 right away
    2. `totalSupply` is set equal to `totalSupply + amount` after a deposit
    """
    AMOUNT = 1000000000000000000
    assert cog_pair.totalSupply() == 0

    account = accounts[0]

    asset.mint(account, AMOUNT, sender=account)
    asset.approve(cog_pair, AMOUNT, sender=account)
    cog_pair.deposit(AMOUNT, account, sender=account)

    assert cog_pair.totalSupply() == AMOUNT

    asset.mint(account, AMOUNT, sender=account)
    asset.approve(cog_pair, AMOUNT, sender=account)
    cog_pair.deposit(AMOUNT, account, sender=account)

    assert cog_pair.totalSupply() == AMOUNT * 2

def test_balanceOf(cog_pair, accounts, asset):
    """"
    Invariants Tested
    -----------------
    1. `balanceOf[msg.sender]` is set equal to `balanceOf[msg.sender] - amount` after a transfer
    2. `balanceOf[to]` is set equal to `balanceOf[to] + amount` after a transfer
    3. `balanceOf[msg.sender]` is set equal to `balanceOf[msg.sender] + amount` after a deposit
    """

    AMOUNT = 1000000000000000000

    account = accounts[0]

    asset.mint(account, AMOUNT, sender=account)
    asset.approve(cog_pair, AMOUNT, sender=account)
    assert cog_pair.balanceOf(account) == 0
    cog_pair.deposit(AMOUNT, account, sender=account)
    assert cog_pair.balanceOf(account) == AMOUNT

    cog_pair.transfer(accounts[1], int(AMOUNT/2), sender=account)

    assert cog_pair.balanceOf(account) == int(AMOUNT/2)

def test_transfer(cog_pair, accounts, asset):
    """"
    Invariants Tested
    -----------------
    1. `balanceOf[msg.sender]` is set equal to `balanceOf[msg.sender] - amount`.
    2. `balanceOf[to]` is set equal to `balanceOf[to] + amount`.
    3. Cannot transfer more funds than they own
    """
    AMOUNT = 1000000000000000000

    account = accounts[0]

    asset.mint(account, AMOUNT, sender=account)
    asset.approve(cog_pair, AMOUNT, sender=account)
    cog_pair.deposit(AMOUNT, account, sender=account)

    cog_pair.transfer(accounts[1], int(AMOUNT/2), sender=account)
    assert cog_pair.balanceOf(account) == int(AMOUNT/2)
    assert cog_pair.balanceOf(accounts[1]) == int(AMOUNT/2)

    with ape.reverts():
        cog_pair.transfer(accounts[1], AMOUNT, sender=account)

def test_transferFrom(cog_pair, accounts, asset):
    """
    Invariants Tested
    -----------------
    1. `balanceOf[from]` is set equal to `balanceOf[from] - amount`.
    2. `balanceOf[to]` is set equal to `balanceOf[to] + amount`.
    3. `allowance[from][msg.sender]` is set equal to `allowance[from][msg.sender] - amount`.
    4. Cannot transfer more funds than they own 
    5. Cannot transfer more funds than they are allowed to

    Also tests approve and allowance implicitly
    """
    AMOUNT = 1000000000000000000

    account = accounts[0]

    asset.mint(account, AMOUNT, sender=account)
    asset.approve(cog_pair, AMOUNT, sender=account)
    cog_pair.deposit(AMOUNT, account, sender=account)

    cog_pair.approve(accounts[1], int(AMOUNT/2), sender=account)

    cog_pair.transferFrom(account, accounts[1], int(AMOUNT/2), sender=accounts[1])

    # `balanceOf[from]` is set equal to `balanceOf[from] - amount`.
    assert cog_pair.balanceOf(account) == int(AMOUNT/2)

    # `balanceOf[to]` is set equal to `balanceOf[to] + amount`.
    assert cog_pair.balanceOf(accounts[1]) == int(AMOUNT/2)

    # `allowance[from][msg.sender]` is set equal to `allowance[from][msg.sender] - amount`.
    assert cog_pair.allowance(account, accounts[1]) == 0

    with ape.reverts():
        # 5. Cannot transfer more funds than they are allowed to
        cog_pair.transferFrom(account, accounts[1], int(AMOUNT/2), sender=accounts[1])
    
    cog_pair.transfer(accounts[0], int(AMOUNT/2), sender=accounts[1])
    with ape.reverts():
        # 4. Cannot transfer more funds than they own 
        cog_pair.transferFrom(account, accounts[1], AMOUNT, sender=accounts[1])


def test_approve_allowance(cog_pair, accounts, asset):
    """
    Invairants Tested
    -----------------
    1. `allowance[msg.sender][spender]` is set equal to `amount`.
    2. `allowance[msg.sender][spender]` is set equal to `amount` after a second approve
    3. `allowance[msg.sender][spender]` is set equal to `0` after a second approve with amount 0
    4. `allowance[msg.sender][spender]` decreased after a transferFrom
    """
    AMOUNT = 1000000000000000000

    account = accounts[0]

    asset.mint(account, AMOUNT, sender=account)
    asset.approve(cog_pair, AMOUNT, sender=account)
    cog_pair.deposit(AMOUNT, account, sender=account)

    cog_pair.approve(accounts[1], int(AMOUNT/2), sender=account)

    # 1. `allowance[msg.sender][spender]` is set equal to `amount`.
    assert cog_pair.allowance(account, accounts[1]) == int(AMOUNT/2)

    cog_pair.approve(accounts[1], 2**256-1, sender=account)

    # 2. `allowance[msg.sender][spender]` is set equal to `amount` after a second approve
    assert cog_pair.allowance(account, accounts[1]) == 2**256-1

    cog_pair.approve(accounts[1], 0, sender=account)

    # 3. `allowance[msg.sender][spender]` is set equal to `0` after a second approve with amount 0
    assert cog_pair.allowance(account, accounts[1]) == 0

    cog_pair.approve(accounts[1], int(AMOUNT/2), sender=account)

    cog_pair.transferFrom(account, accounts[1], int(AMOUNT/2), sender=accounts[1])

    # 4. `allowance[msg.sender][spender]` decreased after a transferFrom
    assert cog_pair.allowance(account, accounts[1]) == 0