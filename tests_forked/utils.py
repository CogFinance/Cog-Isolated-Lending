from ape import Contract, Project
from ape.contracts import ContractContainer


def mint_tokens_for_testing(project: Project, account):
    # CRV
    token_contract = Contract("0xB755039eDc7910C1F1BD985D48322E55A31AC0bF")
    token_owner = "0x0000000000000000000000000000000000000000"
    project.provider.set_balance(token_owner, 10**18)
    token_contract.mint(account, 10 ** 18, sender=token_owner)
    assert token_contract.balanceOf(account.address) >= amount

    # WETH
    weth_contract = Contract("0x5300000000000000000000000000000000000004")
    weth_contract.deposit(value=100 * 10**18, sender=account)
    assert weth_contract.balanceOf(account.address) >= eth_amount * 10**18

