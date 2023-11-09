
import os
from datetime import timedelta
from math import log
from typing import Any, Callable, List

from ape import Contract, Project
import pytest

@pytest.fixture(scope="session")
def account(project, accounts) -> Any:
    accounts[0].balance += int(1e18)
    return accounts[0]

@pytest.fixture(scope="session")
def crv(project, account):
    return project.mock_erc20.at("0xB755039eDc7910C1F1BD985D48322E55A31AC0bF")

@pytest.fixture(scope="session")
def weth(project, account):
    return project.mock_erc20.at("0x5300000000000000000000000000000000000004")

@pytest.fixture(scope="session")
def oracle(project, account):
    return account.deploy(project.LayerZeroOracle, "0x4baa701a4768dc8f7309be7d88fbb6a4529a4985bbf0a00b05bd1205711b5916", "0x8c03583c927c551c0c480da519b38bd4fd858b12dea8ab8e649c5135e00ed78b", 10 ** 25, "0x3DD5C2Acd2F41947E73B384Ef52C049BAc0B65d0")
    
@pytest.fixture(scope="session")
def cog_factory(project, account):
    return project.cog_factory.at("0xbAbD55549c266c6755b99173fE7604238D04117d")

@pytest.fixture(scope="session")
def cog_pair(project, account, cog_factory, oracle, crv, weth):
    return project.cog_pair.at(cog_factory.deploy_medium_risk_pair(weth, crv, oracle, sender=account).events[0].pair)


