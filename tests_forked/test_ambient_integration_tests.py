import ape
import pytest

from datetime import timedelta

from ape import Contract, Project
from ape.contracts import ContractContainer

def mint_tokens_for_testing(project: Project, account):
    # USDC
    token_contract = Contract("0x06eFdBFf2a14a7c8E15944D1F4A48F9F95F663A4")
    token_owner = "0x33B60d5Dd260d453cAC3782b0bDC01ce84672142"
    project.provider.set_balance(token_owner, 100 * 10**18)
    token_contract.mint(account,20000 * 10 ** 18, sender=token_owner)
    assert token_contract.balanceOf(account.address) >= 10 ** 18

    # WETH
    weth_contract = Contract("0x5300000000000000000000000000000000000004")
    weth_contract.deposit(value=100 * 10**18, sender=account)
    assert weth_contract.balanceOf(account.address) >= 1 * 10**18

def test_ambient_oracle(project: Project, usdc, weth, ambient_cog_pair, ambient_oracle, account):
    mint_tokens_for_testing(project, account)
    ambient_oracle.get(sender=account)
    print(ambient_oracle.peekSpot())

    usdc.approve(ambient_cog_pair.address, 1000000 * 10 ** 18, sender=account)
    weth.approve(ambient_cog_pair.address, 1000000 * 10 ** 18, sender=account)

    # 5 CRV collateral
    ambient_cog_pair.add_collateral(account, 2225 * 10 ** 6, sender=account)
    ambient_cog_pair.deposit(5 * 10 ** 18, sender=account)


    BASE_AMOUNT = 1 * 10 ** 18

    with ape.reverts():
        ambient_cog_pair.borrow(int(BASE_AMOUNT), sender=account)

    ambient_cog_pair.borrow(int(BASE_AMOUNT * 0.7), sender=account)

