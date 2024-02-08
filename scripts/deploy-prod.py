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
WSTETH_TOKEN = "0xf610A9dfB7C89644979b4A0f27063E9e7d7Cda32"
USDT_TOKEN = "0xf55BEC9cafDbE8730f096Aa55dad6D22d44099Df"
USDC_TOKEN = "0x06eFdBFf2a14a7c8E15944D1F4A48F9F95F663A4"
DAI_TOKEN = "0xcA77eB3fEFe3725Dc33bccB54eDEFc3D9f764f97"

"""
LayerZero Price Feeds
"""
#LAYERZERO_ORACLE = "0x3DD5C2Acd2F41947E73B384Ef52C049BAc0B65d0"
#ETH_PRICE_FEED = "0x8c03583c927c551c0c480da519b38bd4fd858b12dea8ab8e649c5135e00ed78b"
#CRV_PRICE_FEED = "0x4baa701a4768dc8f7309be7d88fbb6a4529a4985bbf0a00b05bd1205711b5916"
#USDC_PRICE_FEED = "0xbe06225708673194bfdf29a4d5e6278a57cac755e64f4ff5102f77fdf63b7844"
#WSTETH_PRICE_FEED = "0xa827d7b9c9757ba97294e0d662738f64683fdc2713f0c9c929dc6184291c94c4"
#AAVE_PRICE_FEED = "0xabd61589644157a95dfb88a2c28637b590d0723f439a52668767656f6817afe9"


"""
Chainlink Price Feeds
"""
WSTETH_ETH_PRICE_FEED = "0xe428fbdbd61CC1be6C273dC0E27a1F43124a86F3"
ETH_USD_PRICE_FEED = "0x6bF14CB0A831078629D993FDeBcB182b21A8774C"
DAI_USD_PRICE_FEED = "0x203322e1d15EB3Dff541a5aF0288D951c4a8d3eA"
USDC_USD_PRICE_FEED = "0x43d12Fb3AfCAd5347fA764EeAB105478337b7200"
USDT_USD_PRICE_FEED = "0xf376A91Ae078927eb3686D6010a6f1482424954E"
DAI_USDC_PRICE_FEED = "0x203322e1d15EB3Dff541a5aF0288D951c4a8d3eA"

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
    account = accounts.load('bera')
    account.set_autosign(True)

    print(network)

    deployer = account.deploy(project.Deployer, gas_price=1000000000000,type=0)

    blueprint_bytecode = construct_blueprint_deploy_bytecode(project.cog_pair.contract_type.deployment_bytecode.bytecode)
    blueprint_tx = deployer.deploy(blueprint_bytecode, network=network, sender=account)
    blueprint_event = list(blueprint_tx.decode_logs(deployer.Deployed))
    
    blueprint_address = blueprint_event[0].addr

    factory = account.deploy(project.cog_factory, blueprint_address, account, network=network)
    
    loan_router = account.deploy(project.loan_router, network=network)

    print("==========================")
    print("Account Used:             ", account)
    print("Blueprint Address:        ", blueprint_address)
    print("Factory Address:          ", factory.address)
    print("Loan Router Address:      ", loan_router.address)


@cli.command(
    cls=NetworkBoundCommand,
)
@network_option()
def deploy_chainlinkpair(network):
    account = accounts.load('alfa')
    account.set_autosign(True)

    factory = project.cog_factory.at("0xCd44fecb08bb28405992358131Fd5081A0F550D0")

    #usdt_eth = account.deploy(project.ChainlinkOracle, USDT_USD_PRICE_FEED, ETH_USD_PRICE_FEED, 10 ** 6, type=0)
    #factory.deploy_low_risk_pair(USDT_TOKEN, WETH_TOKEN, usdt_eth.address, sender=account, type=0) 

    #usdc_eth = account.deploy(project.ChainlinkOracle, USDC_USD_PRICE_FEED, ETH_USD_PRICE_FEED, 10 ** 6, type=0)
    #factory.deploy_low_risk_pair(USDC_TOKEN, WETH_TOKEN, usdc_eth.address, sender=account, type=0) 

    #dai_eth = account.deploy(project.ChainlinkOracle, DAI_USD_PRICE_FEED, ETH_USD_PRICE_FEED, 10 ** 18, type=0)
    #factory.deploy_low_risk_pair(DAI_TOKEN, WETH_TOKEN, dai_eth.address, sender=account, type=0) 

    #eth_wsteth = account.deploy(project.ChainlinkOracle, "0x0000000000000000000000000000000000000000", WSTETH_ETH_PRICE_FEED, 10 ** 18, type=0)
    #factory.deploy_low_risk_pair(WETH_TOKEN, WSTETH_TOKEN, eth_wsteth.address, sender=account, type=0) 

    #usdt_wsteth = project.TriChainlinkOracle.deploy(USDT_USD_PRICE_FEED, ETH_USD_PRICE_FEED, WSTETH_ETH_PRICE_FEED, 10 ** 18, sender=account, type=0)
    #receipt = factory.deploy_low_risk_pair(USDT_TOKEN, WSTETH_TOKEN, eth_wsteth.address, sender=account, type=0) 
    #wsteth_pair =  "0x" + receipt.logs[0]['topics'][-1].hex()[26:]

    wsteth_usdt = project.TriChainlinkOracleMul.deploy(ETH_USD_PRICE_FEED, WSTETH_ETH_PRICE_FEED, USDT_USD_PRICE_FEED, 10 ** 18, sender=account, type=0)
    receipt = factory.deploy_low_risk_pair(WSTETH_TOKEN, USDT_TOKEN, wsteth_usdt.address, sender=account, type=0) 
    wsteth_usdt_cog_pair = project.cog_pair.at("0x" + receipt.logs[0]['topics'][-1].hex()[26:])

    print("ETH WSTETH: ", wsteth_usdt_cog_pair)
