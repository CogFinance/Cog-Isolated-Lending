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

    if ':local:' in network:
        account = accounts.test_accounts[0]
    account = accounts.test_accounts[0]

    cog_pair_blueprint = construct_blueprint_deploy_bytecode(project.cog_pair.contract_type.deployment_bytecode.bytecode)
    blueprint_address = deploy_blueprint(account, cog_pair_blueprint)
    print(f"Deployed CogPair blueprint to {Fore.GREEN}{blueprint_address}{Style.RESET_ALL} on network {Fore.MAGENTA}{network}{Style.RESET_ALL}")

    # Deploy Factory
    factory = account.deploy(project.cog_factory, blueprint_address, network=network)
    print(f"Deployed CogFactory to {Fore.GREEN}{factory.address}{Style.RESET_ALL} on network {Fore.MAGENTA}{network}{Style.RESET_ALL}")

    # Deploy CogPair from factory
    pair_address_bytes = factory.deploy_medium_risk_pair("0x0000000000000000000000000000000000000001", "0x0000000000000000000000000000000000000001", "0x0000000000000000000000000000000000000001", sender=account).logs[0]['topics'][3]
    pair_address = "0x" + pair_address_bytes.hex()
    print(f"Deployed CogPair to {Fore.GREEN}{pair_address}{Style.RESET_ALL} on network {Fore.MAGENTA}{network}{Style.RESET_ALL}")
