import ape
import pytest

from datetime import timedelta

from ape import Contract, Project
from ape.contracts import ContractContainer


def mint_tokens_for_testing(project: Project, account):
    # CRV
    token_contract = Contract("0xB755039eDc7910C1F1BD985D48322E55A31AC0bF")
    token_owner = "0xE2b4795039517653c5Ae8C2A9BFdd783b48f447A"
    project.provider.set_balance(token_owner, 100 * 10**18)
    token_contract.mint(account,20000 * 10 ** 18, sender=token_owner)
    assert token_contract.balanceOf(account.address) >= 10 ** 18

    # WETH
    weth_contract = Contract("0x5300000000000000000000000000000000000004")
    weth_contract.deposit(value=100 * 10**18, sender=account)
    assert weth_contract.balanceOf(account.address) >= 1 * 10**18


def test_curve_eth_pair(project, weth, aave, account):
    pair = project.cog_pair.at("0x449C58c2F8D2AF6aBe16d0366910b602De430935")
    mint_tokens_for_testing(project, account)
    crv.approve(pair.address, 1000000 * 10 ** 18, sender=account)
    weth.approve(pair.address, 1000000 * 10 ** 18, sender=account)

    # 5 CRV collateral
    pair.add_collateral(account, 2500 * 10 ** 18, sender=account)
    pair.deposit(5 * 10 ** 18, sender=account)


    BASE_AMOUNT = 66 * 10 ** 16

    with ape.reverts():
        pair.borrow(int(BASE_AMOUNT), sender=account)

    pair.borrow(int(BASE_AMOUNT * 0.7), sender=account)
