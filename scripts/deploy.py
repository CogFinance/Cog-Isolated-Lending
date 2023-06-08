from ape import project, accounts, Contract
from ape.cli import NetworkBoundCommand, network_option
# account_option could be used when in prod?
import click
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style
from utils.blueprint import (
    construct_blueprint_deploy_bytecode,
    deploy_blueprint,
    verify_blueprint_deploy_preamble,
    verify_eip522_blueprint,
)

def deploy_factory(deployer, deploy_code):
    transaction = project.provider.network.ecosystem.create_transaction(
        chain_id=project.provider.chain_id,
        data=deploy_code,
        gas_price=project.provider.gas_price,
        nonce=deployer.nonce,
    )

    transaction.gas_limit = project.provider.estimate_gas_cost(transaction)
    signed_transaction = deployer.sign_transaction(transaction)
    receipt = project.provider.send_transaction(signed_transaction)
    return receipt.contract_address

@click.group()
def cli():
    """
    Script for test deployment of CogPair
    """

@cli.command(
    cls=NetworkBoundCommand,
)
@network_option()
def deploy(network):
    colorama_init()

    # Deployer address
    if ':local' in network:
        account = accounts.test_accounts[0]
    else:
        account = accounts.load('alfa')
        account.set_autosign(True)

    kw = {
        'max_fee': project.provider.base_fee * 2,
        'max_priority_fee': int(0.5e9),
        'chain_id': project.provider.chain_id,
        'gas_price': project.provider.gas_price,
    }

    cog_low_pair_blueprint = construct_blueprint_deploy_bytecode(project.cog_low_pair.contract_type.deployment_bytecode.bytecode)
    cog_medium_pair_blueprint = construct_blueprint_deploy_bytecode(project.cog_medium_pair.contract_type.deployment_bytecode.bytecode)
    cog_high_pair_blueprint = construct_blueprint_deploy_bytecode(project.cog_high_pair.contract_type.deployment_bytecode.bytecode)

    cog_stable_pair_blueprint = construct_blueprint_deploy_bytecode(project.cog_stable_pair.contract_type.deployment_bytecode.bytecode)

    low_pair_blueprint_address = deploy_blueprint(account, cog_low_pair_blueprint)
    medium_pair_blueprint_address = deploy_blueprint(account, cog_medium_pair_blueprint)
    high_pair_blueprint_address = deploy_blueprint(account, cog_high_pair_blueprint)

    stable_pair_blueprint_address = deploy_blueprint(account, cog_stable_pair_blueprint)

    # Deploy Factory
    factory = account.deploy(project.cog_factory, stable_pair_blueprint_address, low_pair_blueprint_address, medium_pair_blueprint_address, high_pair_blueprint_address, account, network=network, **kw)

    token_0 = account.deploy(project.mock_erc20, "CogToken0", "CT0", 18, 1000000000000, network=network, **kw)

    token_1 = account.deploy(project.mock_erc20, "CogToken1", "CT1", 18, 1000000000000, network=network, **kw)

    oracle = account.deploy(project.mock_oracle, network=network, **kw)

    receipt = factory.deploy_stable_risk_pair(token_0.address, token_1.address, oracle.address, network=network, sender=account, **kw)
    stable_address = "0x" + receipt.logs[0]['topics'][-1].hex()[26:]

    receipt = factory.deploy_low_risk_pair(token_0.address, token_1.address, oracle.address, network=network, sender=account, **kw)
    low_address = "0x" + receipt.logs[0]['topics'][-1].hex()[26:]

    receipt = factory.deploy_medium_risk_pair(token_0.address, token_1.address, oracle.address, network=network, sender=account, **kw)
    medium_address = "0x" + receipt.logs[0]['topics'][-1].hex()[26:]

    receipt = factory.deploy_high_risk_pair(token_0.address, token_1.address, oracle.address, network=network, sender=account, **kw)
    high_address = "0x" + receipt.logs[0]['topics'][-1].hex()[26:]

    print(f"Deployed the Low Risk Cog Pair Blueprint to {Fore.BLUE}{low_pair_blueprint_address}{Style.RESET_ALL} on network {Fore.MAGENTA}{network}{Style.RESET_ALL}")
    print(f"Deployed the Medium Risk Cog Pair Blueprint to {Fore.BLUE}{medium_pair_blueprint_address}{Style.RESET_ALL} on network {Fore.MAGENTA}{network}{Style.RESET_ALL}")
    print(f"Deployed the High Risk Cog Pair Blueprint to {Fore.BLUE}{high_pair_blueprint_address}{Style.RESET_ALL} on network {Fore.MAGENTA}{network}{Style.RESET_ALL}")
    print(f"Deployed the Stable Cog Pair Blueprint to {Fore.BLUE}{stable_pair_blueprint_address}{Style.RESET_ALL} on network {Fore.MAGENTA}{network}{Style.RESET_ALL}")

    print(f"Deployed CogFactory to {Fore.GREEN}{factory.address}{Style.RESET_ALL} on network {Fore.MAGENTA}{network}{Style.RESET_ALL}")
    print(f"Deployed CogToken0 to {Fore.GREEN}{token_0.address}{Style.RESET_ALL} on network {Fore.MAGENTA}{network}{Style.RESET_ALL}")
    print(f"Deployed CogToken1 to {Fore.GREEN}{token_1.address}{Style.RESET_ALL} on network {Fore.MAGENTA}{network}{Style.RESET_ALL}")
    print(f"Deployed CogOracle to {Fore.GREEN}{oracle.address}{Style.RESET_ALL} on network {Fore.MAGENTA}{network}{Style.RESET_ALL}")

    print(f"Deployed Stable Risk CogPair to {Fore.GREEN}{stable_address}{Style.RESET_ALL} on network {Fore.MAGENTA}{network}{Style.RESET_ALL}")
    print(f"Deployed Low Risk CogPair to {Fore.GREEN}{low_address}{Style.RESET_ALL} on network {Fore.MAGENTA}{network}{Style.RESET_ALL}")
    print(f"Deployed Medium Risk CogPair to {Fore.GREEN}{medium_address}{Style.RESET_ALL} on network {Fore.MAGENTA}{network}{Style.RESET_ALL}")
    print(f"Deployed High Risk CogPair to {Fore.GREEN}{high_address}{Style.RESET_ALL} on network {Fore.MAGENTA}{network}{Style.RESET_ALL}")
