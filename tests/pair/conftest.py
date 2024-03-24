import os
from datetime import timedelta
from math import log
from typing import Any, Callable, List

import boa
import pytest
from hypothesis import settings

@pytest.fixture(scope="session")
def accounts() -> List[Any]:
    return [boa.env.generate_address() for _ in range(11)]

@pytest.fixture(scope="session")
def liquidator(accounts) -> Any:
    return accounts[10]

# TODO: rename to admin and (probably) don't put it in accounts
@pytest.fixture(scope="session")
def account(accounts) -> Any:
    return accounts[0]

@pytest.fixture(scope="session")
def collateral(account):
    with boa.env.prank(account):
        return boa.load('src/mocks/mock_erc20.vy', "Collateral", "CTL", 18)

@pytest.fixture(scope="session")
def asset(account):
    with boa.env.prank(account):
        return boa.load('src/mocks/mock_erc20.vy', "Asset", "ASS", 18)

@pytest.fixture(scope="session")
def oracle(account):
    with boa.env.prank(account):
        return boa.load('src/mocks/mock_oracle.vy')
    
@pytest.fixture(scope="session")
def cog_pair_blueprint(account):
    pair = boa.load_partial('src/cog_pair.vy')
    with boa.env.prank(account):
        return pair.deploy_as_blueprint()

@pytest.fixture(scope="session")
def cog_factory(account, cog_pair_blueprint):
    with boa.env.prank(account):
        return boa.load('src/cog_factory.vy', cog_pair_blueprint, account)

@pytest.fixture(scope="session")
def cog_stable_pair(account, cog_factory, oracle, asset, collateral):
    with boa.env.prank(account):
        pair = boa.load_partial('src/cog_pair.vy')
        return pair.at(cog_factory.deploy_stable_risk_pair(asset, collateral, oracle))

@pytest.fixture(scope="session")
def cog_low_pair(account, cog_factory, oracle, asset, collateral):
    with boa.env.prank(account):
        pair = boa.load_partial('src/cog_pair.vy')
        return pair.at(cog_factory.deploy_low_risk_pair(asset, collateral, oracle))

@pytest.fixture(scope="session")
def cog_pair(account, cog_factory, oracle, asset, collateral):
    with boa.env.prank(account):
        pair = boa.load_partial('src/cog_pair.vy')
        return pair.at(cog_factory.deploy_medium_risk_pair(asset, collateral, oracle))

@pytest.fixture(scope="session")
def cog_high_pair(account, cog_factory, oracle, asset, collateral):
    with boa.env.prank(account):
        pair = boa.load_partial('src/cog_pair.vy')
        return pair.at(cog_factory.deploy_high_risk_pair(asset, collateral, oracle))
