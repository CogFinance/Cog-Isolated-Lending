# ⚙️🐍 Cog-Vyper-Contracts ⚙️🐍

The first implementation of the Cog Finance protocol, written primarily in Vyper. This serves as a spec and benchmark implementation of Cog Finance, implemented with security and simplicity being of the highest concern.

# Installation

To install the repo simply run the commands below (*assuming an install of foundry and python)

- Install [Poetry](https://python-poetry.org/)

```
git submodule init
git submodule update

poetry shell

pip3 install vyper
pip3 install eth-ape

ape plugins install .

forge build
forge test
ape compile
ape test
```

This repo makes full use of Vyper's Swiss Army Knife set of tools, to fully test and analyze the Cog Finance Contracts. The contracts are designed to be battle-hardened, with beyond standard security measures in place.

## Deployment

Contracts can be deployed using the deploy script, which will 

Then in a seperate shell terminal via Deploy the Contracts via

```
ape run scripts/deploy.py deploy --network ethereum:local
```

## Todo

Stuff I would like to finish before big_tech_sux reviews the code

-[ ] Repay overrepay test needs to be added back in, failing for some reason
-[ ] Remove add_asset, remove_asset, in favor of deposit, withdraw, and redeem
-[ ] So so much testing to do with accrue
-[ ] Make negative IR test attacks
-[ ] Ensure PoL accrues properly
-[ ] Add management functions like timelocks, Tinkermaster's ability to withdraw PoL
-[ ] Add full features to the factory
-[ ] fmt one last time

Long-term To-Dos
-[ ] Support approval style usage of shares (deposit, etc)
-[ ] Jade mutation testing
-[ ] State machine testing
-[ ] Low, High, and Stable Risk Pairs

## Contracts

### Cog Pair 

Cog Pair is the main lending pool which powers Cog Finance. It is a relatively simple isolated lending pool which works to balance its interest rate to encourage utilization of the pool between a Minimum and Maximum utilization range. Asset shares are also implemented as an ERC20 for compatbility and composability. The contracts are implemented with emergency measures of both a 2 week timelock, and a pool deposit freeze mechanism. Cog Pools utilize interest rate epochs, directing fees earned to Protocol-Owned liquidity for 3 days after majors spikes in interest rates, this is done to discourage attacks which suddenly spike interest rates to liquidated borrowers at the gain of lenders. The ability to deposit is pausable through an EOA wallet with admin privledges, but upgradability is not possible.

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

### Testing Design

Testing is designed to make use of [Jade](https://github.com/ControlCplusControlV/Jade) for mutation testing, and Foundry for fuzzing.
