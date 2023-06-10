import pytest
import ape

from utils.blueprint import (
    construct_blueprint_deploy_bytecode,
    deploy_blueprint,
    verify_blueprint_deploy_preamble,
    verify_eip522_blueprint,
)

SETTINGS = dict(max_examples=2000)

@pytest.fixture(scope="session")
def account(accounts):
    return accounts[0]

@pytest.fixture(scope="session")
def collateral(account, project):
    token = account.deploy(project.mock_erc20, "Collateral", "CA", "18", 0)
    return token

@pytest.fixture(scope="session")
def asset(account, project):
    token = account.deploy(project.mock_erc20, "Asset", "AB", "18", 0)
    return token

@pytest.fixture(scope="session")
def oracle(account, project):
    oracle = account.deploy(project.mock_oracle)
    return oracle

@pytest.fixture(scope="session")
def cog_pair_blueprint(account, project):
    bytecode = project.cog_pair.contract_type.deployment_bytecode.bytecode
    cog_pair_blueprint = construct_blueprint_deploy_bytecode(bytecode)
    return deploy_blueprint(account, cog_pair_blueprint)


@pytest.fixture(scope="session")
def cog_factory(account, project, cog_pair_blueprint):
    factory = account.deploy(project.cog_factory, cog_pair_blueprint, account)
    return factory


@pytest.fixture(scope="session")
def cog_pair(account, project, cog_factory, collateral, asset, oracle):
    pair_address = cog_factory.deploy_medium_risk_pair(asset, collateral, oracle, sender=account).events[0].pair
    return project.cog_medium_pair.at(pair_address)

@pytest.fixture(scope="session")
def cog_pair_stable(account, project, cog_factory, collateral, asset, oracle):
    pair_address = cog_factory.deploy_stable_risk_pair(asset, collateral, oracle, sender=account).events[0].pair
    return project.cog_stable_pair.at(pair_address)

@pytest.fixture(scope="session")
def cog_pair_low(account, project, cog_factory, collateral, asset, oracle):
    pair_address = cog_factory.deploy_low_risk_pair(asset, collateral, oracle, sender=account).events[0].pair
    return project.cog_low_pair.at(pair_address)

@pytest.fixture(scope="session")
def cog_medium_pair(account, project, cog_factory, collateral, asset, oracle):
    pair_address = cog_factory.deploy_medium_risk_pair(asset, collateral, oracle, sender=account).events[0].pair
    return project.cog_medium_pair.at(pair_address)

@pytest.fixture(scope="session")
def cog_pair_high(account, project, cog_factory, collateral, asset, oracle):
    pair_address = cog_factory.deploy_high_risk_pair(asset, collateral, oracle, sender=account).events[0].pair
    return project.cog_high_pair.at(pair_address)
