from ape import project, accounts, Contract
from ape.cli import NetworkBoundCommand, network_option
# account_option could be used when in prod?
import click
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

"""
Constant Addresses for Deployment
"""
FACTORY_MAINNET = "0xbAbD55549c266c6755b99173fE7604238D04117d"
CRV_TOKEN = "0xB755039eDc7910C1F1BD985D48322E55A31AC0bF"
WETH_TOKEN = "0x5300000000000000000000000000000000000004"
AAVE_TOKEN = "0x79379C0E09a41d7978f883a56246290eE9a8c4d3"

"""
LayerZero Price Feeds
"""
LAYERZERO_ORACLE = "0x3DD5C2Acd2F41947E73B384Ef52C049BAc0B65d0"
ETH_PRICE_FEED = "0x8c03583c927c551c0c480da519b38bd4fd858b12dea8ab8e649c5135e00ed78b"
CRV_PRICE_FEED = "0x4baa701a4768dc8f7309be7d88fbb6a4529a4985bbf0a00b05bd1205711b5916"
USDC_PRICE_FEED = "0xbe06225708673194bfdf29a4d5e6278a57cac755e64f4ff5102f77fdf63b7844"
WSTETH_PRICE_FEED = "0xa827d7b9c9757ba97294e0d662738f64683fdc2713f0c9c929dc6184291c94c4"
AAVE_PRICE_FEED = "0xabd61589644157a95dfb88a2c28637b590d0723f439a52668767656f6817afe9"

@click.group()
def cli():
    """
    Script for test deployment of CogPair
    """

@cli.command(
    cls=NetworkBoundCommand,
)
@network_option()
def deploy_core_contracts(network):
    account = accounts.load('mainnet')
    account.set_autosign(True)

    deployer = account.deploy(project.Deployer, type=0)

    blueprint_bytecode = construct_blueprint_deploy_bytecode(project.cog_pair.contract_type.deployment_bytecode.bytecode)
    blueprint_tx = deployer.deploy(blueprint_bytecode, type=0, network=network, sender=account)
    blueprint_event = list(blueprint_tx.decode_logs(deployer.Deployed))
    
    blueprint_address = blueprint_event[0].addr

    factory = account.deploy(project.cog_factory, blueprint_address, account, type=0, network=network)
    
    loan_router = account.deploy(project.loan_router, type=0, network=network)

    print("==========================")
    print("Account Used:             ", account)
    print("Blueprint Address:        ", blueprint_address)
    print("Factory Address:          ", factory.address)
    print("Loan Router Address:      ", loan_router.address)


@cli.command(
    cls=NetworkBoundCommand,
)
@network_option()
def deploy_layerZeroPair(network):
    account = accounts.load('alfa')
    account.set_autosign(True)

    factory = project.cog_factory.at(FACTORY_MAINNET)

    # 18 decimals is default, +/- depending upon the difference in price_feeds
    oracle = account.deploy(project.LayerZeroOracle, ETH_PRICE_FEED, AAVE_PRICE_FEED, 10 ** 18, LAYERZERO_ORACLE, type=0)

    factory.deploy_high_risk_pair(WETH_TOKEN, AAVE_TOKEN, oracle.address, sender=account, type=0) 
