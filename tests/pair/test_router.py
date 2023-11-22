import pytest
import boa

from datetime import timedelta

from hypothesis import (
    given,
    settings,
    strategies as st,
)

# Since the router can use up to 5 pairs, we need 5 fixtures for potential pools

@pytest.fixture(scope="session")
def collateral_0(account):
    with boa.env.prank(account):
        return boa.load('src/mocks/mock_erc20.vy', "Collateral", "CTL", 18)

@pytest.fixture(scope="session")
def collateral_1(account):
    with boa.env.prank(account):
        return boa.load('src/mocks/mock_erc20.vy', "Collateral", "CTL", 18)

@pytest.fixture(scope="session")
def collateral_2(account):
    with boa.env.prank(account):
        return boa.load('src/mocks/mock_erc20.vy', "Collateral", "CTL", 18)

@pytest.fixture(scope="session")
def collateral_3(account):
    with boa.env.prank(account):
        return boa.load('src/mocks/mock_erc20.vy', "Collateral", "CTL", 18)

@pytest.fixture(scope="session")
def collateral_4(account):
    with boa.env.prank(account):
        return boa.load('src/mocks/mock_erc20.vy', "Collateral", "CTL", 18)

@pytest.fixture(scope="session")
def cog_pair_0(account, cog_factory, oracle, collateral_1, collateral_0):
    with boa.env.prank(account):
        pair = boa.load_partial('src/cog_pair.vy')
        return pair.at(cog_factory.deploy_medium_risk_pair(collateral_1, collateral_0, oracle))

@pytest.fixture(scope="session")
def cog_pair_1(account, cog_factory, oracle, collateral_2, collateral_1):
    with boa.env.prank(account):
        pair = boa.load_partial('src/cog_pair.vy')
        return pair.at(cog_factory.deploy_medium_risk_pair(collateral_2, collateral_1, oracle))

@pytest.fixture(scope="session")
def cog_pair_2(account, cog_factory, oracle, collateral_3, collateral_2):
    with boa.env.prank(account):
        pair = boa.load_partial('src/cog_pair.vy')
        return pair.at(cog_factory.deploy_medium_risk_pair(collateral_3, collateral_2, oracle))

@pytest.fixture(scope="session")
def cog_pair_3(account, cog_factory, oracle, collateral_4, collateral_3):
    with boa.env.prank(account):
        pair = boa.load_partial('src/cog_pair.vy')
        return pair.at(cog_factory.deploy_medium_risk_pair(collateral_4, collateral_3, oracle))

def test_router_works(accounts, loan_router, collateral_0, collateral_1, collateral_2, collateral_3, collateral_4, cog_pair_0, cog_pair_1, cog_pair_2, cog_pair_3):
    account = accounts[1]

    collateral_1.mint(account, 100 * 10 ** 18, sender=account)
    collateral_1.approve(cog_pair_0, 100 * 10 ** 18, sender=account)
    cog_pair_0.deposit(100 * 10 ** 18, account, sender=account)

    collateral_2.mint(account, 100 * 10 ** 18, sender=account)
    collateral_2.approve(cog_pair_1, 100 * 10 ** 18, sender=account)
    cog_pair_1.deposit(100 * 10 ** 18, account, sender=account)

    collateral_3.mint(account, 100 * 10 ** 18, sender=account)
    collateral_3.approve(cog_pair_2, 100 * 10 ** 18, sender=account)
    cog_pair_2.deposit(100 * 10 ** 18, account, sender=account)

    collateral_4.mint(account, 100 * 10 ** 18, sender=account)
    collateral_4.approve(cog_pair_3, 100 * 10 ** 18, sender=account)
    cog_pair_3.deposit(100 * 10 ** 18, account, sender=account)

    account = accounts[2]
    collateral_0.mint(account, 100 * 10 ** 18, sender=account)
    collateral_0.approve(loan_router.address, 100 * 10 ** 18, sender=account)
    
    hop_one = (cog_pair_0.address, 100 * 10 ** 18, 50 * 10 ** 18)
    hop_two = (cog_pair_1.address, 50 * 10 ** 18, 25 * 10 ** 18)
    hop_three = (cog_pair_2.address, 25 * 10 ** 18, 12 * 10 ** 18)
    hop_four = (cog_pair_3.address, 12 * 10 ** 18, 6 * 10 ** 18)
    hop_five = ("0x0000000000000000000000000000000000000000", 0, 0)

    cog_pair_0.approve_borrow(loan_router.address, 2**256 -1, sender=account)
    cog_pair_1.approve_borrow(loan_router.address, 2**256 -1, sender=account)
    cog_pair_2.approve_borrow(loan_router.address, 2**256 -1, sender=account)
    cog_pair_3.approve_borrow(loan_router.address, 2**256 -1, sender=account)

    loan_router.loan_tokens([hop_one, hop_two, hop_three, hop_four, hop_five], 2 ** 256 -1, sender=account)

    assert collateral_4.balanceOf(account) > 0
    assert cog_pair_3.user_borrow_part(account) > 0
    
