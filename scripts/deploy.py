from ape import project, accounts, Contract
from ape.cli import NetworkBoundCommand, network_option
# account_option could be used when in prod?
import click
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style
from web3 import Web3, HTTPProvider
from hexbytes import HexBytes

EIP_5202_EXECUTION_HALT_BYTE = bytes.fromhex("fe")
EIP_5202_BLUEPRINT_IDENTIFIER_BYTE = bytes.fromhex("71")
EIP_5202_VERSION_BYTE = bytes.fromhex("00")

# Bytecode preamble is not deployed on-chain
# To properly deploy a blueprint contract, special deploy bytecode must be used.
# The following preamble, prepended to regular deploy bytecode (output of vyper -f bytecode),
# should deploy the blueprint in an ordinary contract creation transaction.
# For more details: https://docs.vyperlang.org/en/stable/built-in-functions.html#create_from_blueprint
# To check the deploy bytecode, run vyper -f blueprint_bytecode contracts/GateSeal.vy

# OPERATIONS
# deploy_preamble = "61" + bytecode len in 2 bytes + "3d81600a3d39f3"
# 61  PUSH2 BYTECODE_LENGTH_2_BYTES: STACK 
# 3D  RETURNDATASIZE
# 81  DUP2
# 60  PUSH1 0x0a
# 3D  RETURNDATASIZE
# 39  CODECOPY 
# F3  *RETURN
DEPLOY_PREAMBLE_BYTE_LENGTH = 10
DEPLOY_PREAMBLE_INITIAL_BYTE = bytes.fromhex("61")
DEPLOY_PREABLE_POST_LENGTH_BYTES = bytes.fromhex("3d81600a3d39f3")


def construct_blueprint_deploy_bytecode(initial_gateseal_bytecode: str):
    eip_5202_bytecode = (
        EIP_5202_EXECUTION_HALT_BYTE
        + EIP_5202_BLUEPRINT_IDENTIFIER_BYTE
        + EIP_5202_VERSION_BYTE
        + bytes.fromhex(initial_gateseal_bytecode[2:])
    )

    with_deploy_preamble = (
        DEPLOY_PREAMBLE_INITIAL_BYTE
        + bytes.fromhex(len(eip_5202_bytecode).to_bytes(2, "big").hex())
        + DEPLOY_PREABLE_POST_LENGTH_BYTES
        + eip_5202_bytecode
    )

    return with_deploy_preamble

@click.group()
def cli():
    """
    Script for test deployment of CogPair
    """

@cli.command(
    cls=NetworkBoundCommand,
)
@network_option()
def deploy_blueprint(network):
    colorama_init()

    # Deployer address
    if ':local' in network:
        account = accounts.test_accounts[0]
    else:
        account = accounts.load('alfa')
        account.set_autosign(True)

    deployer = account.deploy(project.Deployer, type=0)

    blueprint_bytecode = construct_blueprint_deploy_bytecode(project.cog_pair.contract_type.deployment_bytecode.bytecode)
    blueprint_tx = deployer.deploy(blueprint_bytecode, type=0, network=network, sender=account)
    blueprint_event = list(blueprint_tx.decode_logs(deployer.Deployed))
    
    blueprint_address = blueprint_event[0].addr

    print("==================================================")
    print(" Deployed Cog Pair Blueprint to {0}".format(blueprint_address))
    print("==================================================")

@cli.command(
    cls=NetworkBoundCommand,
)
@network_option()
def deploy_factory(network, blueprint_address):
    colorama_init()

    # Deployer address
    if ':local' in network:
        account = accounts.test_accounts[0]
    else:
        account = accounts.load('alfa')
        account.set_autosign(True)

    factory = account.deploy(project.cog_factory, blueprint_address, account, type=0, network=network)

    print("==================================================")
    print(" Deployed Cog Factory to {0}".format(factory.address))
    print("==================================================")

@cli.command(
    cls=NetworkBoundCommand,
)
@network_option()
def deploy_chainlink_oracle(network, _mul, _div, _dec, _uptime_feed):
    colorama_init()

    # Deployer address
    if ':local' in network:
        account = accounts.test_accounts[0]
    else:
        account = accounts.load('alfa')
        account.set_autosign(True)

    oracle = account.deploy(project.ChainlinkOracle, _mul, _div, _dec, _uptime_feed, type=0, network=network)

@cli.command(
    cls=NetworkBoundCommand,
)
@network_option()
def deploy_poolsharks_oracle(network, _pool, _token):
    colorama_init()

    # Deployer address
    if ':local' in network:
        account = accounts.test_accounts[0]
    else:
        account = accounts.load('alfa')
        account.set_autosign(True)

    oracle = account.deploy(project.PoolSharksOracle, _pool, _token, type=0, network=network)

@cli.command(
    cls=NetworkBoundCommand,
)
@network_option()
def sepolia_testnet_deploy(network):
    account = accounts.load('alfa')
    account.set_autosign(True)

    deployer = account.deploy(project.Deployer, type=0)

    blueprint_bytecode = construct_blueprint_deploy_bytecode(project.cog_pair.contract_type.deployment_bytecode.bytecode)
    blueprint_tx = deployer.deploy(blueprint_bytecode, type=0, network=network, sender=account)
    blueprint_event = list(blueprint_tx.decode_logs(deployer.Deployed))
    
    blueprint_address = blueprint_event[0].addr

    factory = account.deploy(project.cog_factory, blueprint_address, account, type=0, network=network)

    oracle = account.deploy(project.PoolSharksOracle, type=0, network=network)

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

    deployer = account.deploy(project.Deployer, type=0)

    blueprint_bytecode = construct_blueprint_deploy_bytecode(project.cog_pair.contract_type.deployment_bytecode.bytecode)
    blueprint_tx = deployer.deploy(blueprint_bytecode, type=0, network=network, sender=account)
    blueprint_event = list(blueprint_tx.decode_logs(deployer.Deployed))
    
    blueprint_address = blueprint_event[0].addr

    print("==================================================")
    print(" Deployed Cog Pair Blueprint to {0}".format(blueprint_address))
    print("==================================================")

    factory = account.deploy(project.cog_factory, blueprint_address, account, type=0, network=network)

    print("==================================================")
    print(" Deployed Cog Factory to {0}".format(factory.address))
    print("==================================================")
    
    # Ether/USD oracle
    oracle = account.deploy(project.ChainlinkOracle, "0x33e87B12b4694DE88D8D2e033a3Cad1F532Db2fb", "0x0000000000000000000000000000000000000000", 18, type=0, network=network)

    print("==================================================")
    print(" Deployed Mock Oracle to {0}".format(oracle.address))
    print("==================================================")
    
    mock_ether = account.deploy(project.mock_erc20, "Ether", "ETH", 18, type=0, network=network)
    mock_stable = account.deploy(project.mock_erc20, "Stable", "USD", 18, type=0, network=network)

    print("==================================================")
    print(" Deployed Mock WETH to {0}".format(mock_ether.address))
    print(" Deployed Mock USD to {0}".format(mock_stable.address))
    print("==================================================")

    pair_tx = factory.deploy_medium_risk_pair(mock_ether.address, mock_stable.address, oracle.address, type=0, sender=account, network=network)
    pair_addr = list(pair_tx.decode_logs(factory.MediumPairCreated))[0].pair

    print("==================================================")
    print(" Deployed Med Risk Pair to {0}".format(pair_addr))
    print("==================================================")
    
    # pair_instance = project.cog_pair.at(pair_addr)

    # result = pair_instance.get_exchange_rate(type=0, network=network, sender=account)

    mint_ether_tx = mock_ether.mint(account.address, 10 ** 9 * 10 ** 18, type=0, sender=account, network=network)
    mint_stable_tx = mock_stable.mint(account.address, 10 ** 9 * 10 ** 18, type=0, sender=account, network=network)

    print("==================================================")
    print(" Minted Mock Tokens")
    print("==================================================")

    loan_router = account.deploy(project.loan_router, type=0, network=network)

    print("==================================================")
    print(" Deployed Loan Router to {0}".format(loan_router.address))
    print("==================================================")
