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

@click.group()
def cli():
    """
    Script for test deployment of CogPair
    """

@cli.command(
    cls=NetworkBoundCommand,
)
@network_option()
def deploy_mock_tokens(network):
    account = accounts.load('alfa')
    account.set_autosign(True)
    
    mock_usdc = account.deploy(project.mock_erc20, "USDC", "USDC", 6, type=0, network=network)
    mock_dai = account.deploy(project.mock_erc20, "DAI", "DAI", 18, type=0, network=network)
    mock_stETH = account.deploy(project.mock_erc20, "wstETH", "wstETH", 18, type=0, network=network)
    mock_mevETH = account.deploy(project.mock_erc20, "mevETH", "mevETH", 18, type=0, network=network)
    mock_yETH = account.deploy(project.mock_erc20, "yETH", "yETH", 18, type=0, network=network)

    mock_yfi = account.deploy(project.mock_erc20, "Yearn", "YFI", 18, type=0, network=network)
    mock_sushi = account.deploy(project.mock_erc20, "Sushi", "SUSHI", 18, type=0, network=network)

    print("=======================")
    print("Mock USDC:  ", mock_usdc.address)
    print("Mock DAI:   ", mock_dai.address)
    print("Mock stETH: ", mock_stETH.address)
    print("Mock yETH:  ", mock_yETH.address)
    print("Mock YFI:   ", mock_yfi.address)
    print("Mock Sushi: ", mock_sushi.address)

@cli.command(
    cls=NetworkBoundCommand,
)
@network_option()
def deploy(network):
    account = accounts.load('alfa')
    account.set_autosign(True)

    deployer = account.deploy(project.Deployer, type=0)

    blueprint_bytecode = construct_blueprint_deploy_bytecode(project.cog_pair.contract_type.deployment_bytecode.bytecode)
    blueprint_tx = deployer.deploy(blueprint_bytecode, type=0, network=network, sender=account)
    blueprint_event = list(blueprint_tx.decode_logs(deployer.Deployed))
    
    blueprint_address = blueprint_event[0].addr

    factory = account.deploy(project.cog_factory, blueprint_address, account, type=0, network=network)
    
    loan_router = account.deploy(project.loan_router, type=0, network=network)

    print("==========================")
    print("Blueprint Address:        ", blueprint_address)
    print("Factory Address:          ", factory.address)
    print("Loan Router Address:      ", loan_router.address)
