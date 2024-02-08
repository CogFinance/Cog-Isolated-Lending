
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
def usdc(project, account):
    return project.mock_erc20.at("0x06eFdBFf2a14a7c8E15944D1F4A48F9F95F663A4")

@pytest.fixture(scope="session")
def usdt(project, account):
    return project.mock_erc20.at("0xf55BEC9cafDbE8730f096Aa55dad6D22d44099Df")

@pytest.fixture(scope="session")
def dai(project, account):
    return project.mock_erc20.at("0xcA77eB3fEFe3725Dc33bccB54eDEFc3D9f764f97")

@pytest.fixture(scope="session")
def weth(project, account):
    return project.mock_erc20.at("0x5300000000000000000000000000000000000004")

@pytest.fixture(scope="session")
def wsteth(project, account):
    return project.mock_erc20.at("0xf610A9dfB7C89644979b4A0f27063E9e7d7Cda32")

@pytest.fixture(scope="session")
def lz_oracle(project, account):
    return account.deploy(project.LayerZeroOracle, "0x8c03583c927c551c0c480da519b38bd4fd858b12dea8ab8e649c5135e00ed78b", "0x4baa701a4768dc8f7309be7d88fbb6a4529a4985bbf0a00b05bd1205711b5916", 10 ** 18, "0x3DD5C2Acd2F41947E73B384Ef52C049BAc0B65d0")

@pytest.fixture(scope="session")
def ambient_oracle(project, account):
    return account.deploy(project.AmbientOracle, "0x62223e90605845Cf5CC6DAE6E0de4CDA130d6DDf", "0x0000000000000000000000000000000000000000", "0x06eFdBFf2a14a7c8E15944D1F4A48F9F95F663A4", "0x0000000000000000000000000000000000000000")

@pytest.fixture(scope="session")
def cog_factory(project, account):
    return project.cog_factory.at("0xbAbD55549c266c6755b99173fE7604238D04117d")

@pytest.fixture(scope="session")
def ambient_cog_pair(project, account, cog_factory, weth, usdc, ambient_oracle):
    return project.cog_pair.at(cog_factory.deploy_stable_risk_pair(weth, usdc, ambient_oracle, sender=account).events[0].pair)

