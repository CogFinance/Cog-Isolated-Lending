import ape
import pytest

from datetime import timedelta

from ape import Contract, Project
from ape.contracts import ContractContainer

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


def mint_tokens_for_testing(project: Project, account):
    project.provider.set_balance(account, 500 * 10**18)

    # WETH
    weth_contract = Contract("0x5300000000000000000000000000000000000004")
    weth_contract.deposit(value=100 * 10**18, sender=account)

def test_chainlink_oracle(project: Project, usdc, wsteth, usdt, dai, weth):
    account = "0x7160570BB153Edd0Ea1775EC2b2Ac9b65F1aB61B"
    mint_tokens_for_testing(project, account)
    usdt_cog_pair = project.cog_pair.at("0x4Ac126e5dd1Cd496203a7E703495cAa8112A20cA")
    usdc_cog_pair = project.cog_pair.at("0x63FdAFA50C09c49F594f47EA7194b721291ec50f")
    dai_cog_pair = project.cog_pair.at("0x43187A6052A4BF10912CDe2c2f94953e39FcE8c7")
    wsteth_cog_pair = project.cog_pair.at("0x344f0B7D0c654F4E58F8B4727813BE86b85DEf3A")
    usdt_wsteth_cog_pair =  project.cog_pair.at("0x5c121db888ad212670017080047ed16ce99a2a96")
    wsteth_usdt_cog_pair = project.cog_pair.at("0xE04a78DC12Bd6969125B6bEb75e26Ce61d95cbaC")


    #factory = project.cog_factory.at("0xCd44fecb08bb28405992358131Fd5081A0F550D0")

    #eth_wsteth = project.TriChainlinkOracleMul.deploy(ETH_USD_PRICE_FEED, WSTETH_ETH_PRICE_FEED, USDT_USD_PRICE_FEED, 10 ** 18, sender=account, type=0)
    #receipt = factory.deploy_low_risk_pair(WSTETH_TOKEN, USDT_TOKEN, eth_wsteth.address, sender=account, type=0) 
    #wsteth_usdt_cog_pair = project.cog_pair.at("0x" + receipt.logs[0]['topics'][-1].hex()[26:])


    usdt.approve(wsteth_usdt_cog_pair.address, 1000000 * 10 ** 18, sender=account)
    wsteth.approve(usdt_wsteth_cog_pair.address, 1000000 * 10 ** 18, sender=account)
    wsteth.approve(wsteth_cog_pair.address, 1000000 * 10 ** 18, sender=account)
    weth.approve(usdt_cog_pair.address, 1000000 * 10 ** 18, sender=account)
    weth.approve(usdc_cog_pair.address, 1000000 * 10 ** 18, sender=account)
    weth.approve(dai_cog_pair.address, 1000000 * 10 ** 18, sender=account)

    wsteth.approve(wsteth_usdt_cog_pair.address, 1000000 * 10 ** 18, sender=account)
    usdt.approve(usdt_wsteth_cog_pair.address, 1000000 * 10 ** 18, sender=account)
    weth.approve(wsteth_cog_pair.address, 1000000 * 10 ** 18, sender=account)
    usdt.approve(usdt_cog_pair.address, 1000000 * 10 ** 18, sender=account)
    usdc.approve(usdc_cog_pair.address, 1000000 * 10 ** 18, sender=account)
    dai.approve(dai_cog_pair.address, 1000000 * 10 ** 18, sender=account)

    # 1 ETH Collateral
    wsteth_usdt_cog_pair.add_collateral(account, 2805 * 10 ** 6, sender=account)
    wsteth_cog_pair.add_collateral(account, 1 * 10 ** 18, sender=account)
    usdc_cog_pair.add_collateral(account, 1 * 10 ** 18, sender=account)
    usdt_cog_pair.add_collateral(account, 1 * 10 ** 18, sender=account)
    dai_cog_pair.add_collateral(account, 1 * 10 ** 18, sender=account)
    usdt_wsteth_cog_pair.add_collateral(account, 1 * 10 ** 18, sender=account)

    wsteth_usdt_cog_pair.deposit(10 * 10 ** 18, sender=account)
    usdc_cog_pair.deposit(5000 * 10 ** 6, sender=account)
    usdt_cog_pair.deposit(5000 * 10 ** 6, sender=account)
    dai_cog_pair.deposit(5000 * 10 ** 18, sender=account)
    wsteth_cog_pair.deposit(10 * 10 ** 18, sender=account)
    usdt_wsteth_cog_pair.deposit(5000 * 10 ** 6, sender=account)

    BASE_AMOUNT = 2805 * 10 ** 6

    with ape.reverts():
        usdt_wsteth_cog_pair.borrow(int(BASE_AMOUNT * 0.9), sender=account)

    usdt_wsteth_cog_pair.borrow(int(100 * 0.8), sender=account)

    BASE_AMOUNT = 2805 * 10 ** 18

    usdt_wsteth_cog_pair.get_exchange_rate(sender=account)
    print(usdt_wsteth_cog_pair.exchange_rate())

    with ape.reverts():
        usdt_wsteth_cog_pair.borrow(int(BASE_AMOUNT * 0.9), sender=account)

    usdt_wsteth_cog_pair.borrow(int(100 * 0.8), sender=account)

    BASE_AMOUNT = 2433 * 10 ** 6
   
    with ape.reverts():
        usdt_cog_pair.borrow(int(BASE_AMOUNT * 0.9), sender=account)

    usdt_cog_pair.borrow(int(BASE_AMOUNT * 0.8), sender=account)

    with ape.reverts():
        usdc_cog_pair.borrow(int(BASE_AMOUNT * 0.9), sender=account)

    usdc_cog_pair.borrow(int(BASE_AMOUNT * 0.8), sender=account)

    BASE_AMOUNT = 2424 * 10 ** 18
    
    with ape.reverts():
        dai_cog_pair.borrow(int(BASE_AMOUNT * 0.9), sender=account)

    dai_cog_pair.borrow(int(BASE_AMOUNT * 0.8), sender=account)

    BASE_AMOUNT = int(1.12 * 10 ** 18)

    with ape.reverts():
        wsteth_cog_pair.borrow(int(BASE_AMOUNT * 0.9), sender=account)

    wsteth_cog_pair.borrow(int(BASE_AMOUNT * 0.8), sender=account)
