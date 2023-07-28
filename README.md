# ⚙️🐍 Cog-Vyper-Contracts ⚙️🐍

The first implementation of the Cog Finance protocol, written primarily in Vyper. This serves as a spec and benchmark implementation of Cog Finance, implemented with security and simplicity being of the highest concern.

# Installation

This repo makes full use of Vyper's Swiss Army Knife set of tools, to fully test and analyze the Cog Finance Contracts. The contracts are designed to be battle-hardened, with beyond standard security measures in place.

## Testing

Tests can be run from a fresh venv via the following commands
```shell
python3 -m venv test_env
source deploy_env/bin/activate

pip3 install titanoboa
pip3 install hypothesis
pip3 install pytest-cov
pip3 install pytest

pytest -s --cov=src/ tests/
coverage html
pytest . 
```

## Deployment

Contracts can be deployed using the deploy script, which can run from a fresh venv via the follow commands

```shell
python3 -m venv deploy_env
source deploy_env/bin/activate

pip3 install eth-ape
pip3 install colorama
pip3 install web3
pip3 install click

ape plugins install .
ape compile
ape run scripts/deploy.py deploy --network https://alpha-rpc.scroll.io/l2
```

## Contracts

### Cog Pair 

Cog Pair is the main lending pool which powers Cog Finance. It is a relatively simple isolated lending pool which works to balance its interest rate to encourage utilization of the pool between a Minimum and Maximum utilization range. Asset shares are also implemented as an ERC20 for compatibility and composability. The contracts are implemented with emergency measures of both a 2 week timelock, and a pool deposit freeze mechanism. Cog Pools utilize interest rate epochs, directing fees earned to Protocol-Owned liquidity for 3 days after majors spikes in interest rates, this is done to discourage attacks which suddenly spike interest rates to liquidated borrowers at the gain of lenders. The ability to deposit is pausable through an EOA wallet with admin priviledges, but upgradability is not possible.

#### Supported Interfaces 
- [ERC20](https://eips.ethereum.org/EIPS/eip-20)
- [ERC4626](https://eips.ethereum.org/EIPS/eip-4626)

### Cog Factory

The factory which handles the deployment of the Cog Pairs. The factory works by deploying through Blueprint Contracts of each Cog Pair type. Each deployment is then tracked by the factory, which is ultimately in control of the Protocol-Owned liquidity each pair accrues. This will then be used for future Tinkermaster expansion. The deployment of new pools is pausable through a EOA controled timelock.

#### Supported Interfaces
- [Blueprint](https://eips.ethereum.org/EIPS/eip-5202)

## External Integrations and Testing

### Supported Protocols

To allow the most flexible deployment of Cog, this repo prepares several integrations in mind, primarily [Bunni](https://github.com/zeframlou/bunni) for leveraged liquidity provision, and [Uniswap V3 TWAP](https://github.com/Uniswap/v3-core/blob/main/contracts/UniswapV3Pool.sol#L236).

## Testing Design

### Coverage

**ERC20 Functions**

- [totalSupply](./tests/test_erc20_interface.py#L18)
- [balanceOf](./tests/test_erc20_interface.py#L46)
- [transfer](./tests/test_erc20_interface.py#76)
- [transferFrom](./tests/test_erc20_interface.py#107)
- [approve](./tests/test_erc20_interface.py#158)
- [allowance](./tests/test_erc20_interface.py#158)

**ERC 2612 Functions**

- [permit](./test//core_tests/Permit.t.sol)

**ERC 4626**
- [asset](./tests/test_erc4626_interface.py#18)
- [totalAssets](./tests/test_erc4626_interface.py#21)
- [convertToShares](./tests/test_erc4626_interface.py#87)
- [convertToAssets](./tests/test_erc4626_interface.py#145)
- [maxDeposit](./tests/test_erc4626_interface.py#193)
- [previewDeposit](./tests/test_erc4626_interface.py#205)
- [deposit](./tests/test_erc4626_interface.py#249)
- [maxMint](./tests/test_erc4626_interface.py#285)
- [previewMint](./tests/test_erc4626_interface.py#293)
- [mint](./tests/test_erc4626_interface.py#347)
- [maxWithdraw](./tests/test_erc4626_interface.py#406)
- [previewWithdraw](./tests/test_erc4626_interface.py#444) 
- [withdraw](./tests/test_erc4626_interface.py#486)
- [maxRedeem](./tests/test_erc4626_interface.py#549)
- [previewRedeem](./tests/test_erc4626_interface.py#599) 
- [redeem](./tests/test_erc4626_interface.py#639)

**General Functions**
- [liquidate](./tests/test_liquidation_invariants.py)
- [borrow](./tests/test_borrow_invariants.py)
- [repay](./tests/test_repay_invariants.py)
- [add_collateral](./tests/test_collateral_invariants.py#19)
- [remove_collateral](./tests/test_collateral_invariants.py#83)
- [Fee Logic for Pol](./tests/test_protocol_fees.py)
