# ⚙️🐍 Cog-Vyper-Contracts ⚙️🐍

The first implementation of the Cog Finance protocol, written primarily in Vyper. This serves as a spec and benchmark implementation of Cog Finance, implemented with security and simplicity being of the highest concern.

To install the repo simply run the commands below (*assuming an install of foundry and python)

```
git submodule init
git submodule update

pip3 install vyper

forge build
forge test
```

This repo makes full use of Vyper's Swiss Army Knife set of tools, to fully test and analyze the Cog Finance Contracts. The contracts are designed to be battle-hardened, with beyond standard security measures in place.

## Contracts

### Cog Pair 

Cog Pair is the main lending pool which powers Cog Finance. It is a relatively simple isolated lending pool which works to balance its interest rate to encourage utilization of the pool between a Minimum and Maximum utilization range. Asset shares are also implemented as an ERC20 for compatbility and composability. The contracts are implemented with emergency measures of both a 2 week timelock, and a pool deposit freeze mechanism. Cog Pools utilize interest rate epochs, directing fees earned to Protocol-Owned liquidity for 3 days after majors spikes in interest rates, this is done to discourage attacks which suddenly spike interest rates to liquidated borrowers at the gain of lenders.

### Cog Factory (v1)

Cog Factory is a factory contract to deploy Cog Pairs, with a pre-defined set of parameter groupings, for pools which fit certain criteria, such as stable, low, medium, and high risk asset pairs. Factory versions will be displayed here, with each new Factory version coming with a new set of groupings, we reccomend indivudally indexing each Factory.

### Cog Route

The Cog Route manages deposits between multiple Cog pairs based on some pre-defined parameters to ensure maximum yield is being earned from borrowing, and that capital is being allocated efficiently.

## Tools 

In order to ensure the Cog Contracts are of the highest quality possible, several tools and templates were used, special thanks to

- [Gambit Mutation Testing](https://medium.com/certora/gambit-23ef5cab02f5)
- [Titanboa for Modeling](https://github.com/vyperlang/titanoboa)
- [Foundry For Fuzz Testing](https://github.com/foundry-rs/foundry)
