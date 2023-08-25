# Deployment Instructions

## Chainlink Oracles Must Match
Issue brought up in the audit is described below for how scaling should work but chainlink feed used should either only be usd-based or eth-based within an oracle, and decimals must be properly adjusted depending upon that.

```
multiply address and divide address are both provided:
price = 1e36*mulPrice/(divPrice*decimals)
This requires the mulPrice and divPrice to have the same decimals. multiply and divide have to both be either eth-based chainlink price feed or usd-based price feed. And the decimals defined in the contract should be 1e18.
e.g: aave-usd/uni-usd ⇒ aave/uni price oracle
multiply address is not provided and divide address is provided
price = 1e36*1e18/(divPrice*decimals)
    divPrice is eth-based chainlink price feed (1e18 decimals): the decimals defined in the contract should be 1e18
    divPrice is usd-based chainlink price feed (1e8 decimals): the decimals defined in the contract should be 1e28
multiply address is provided and divide address is not provided
price = 1e36*mulPrice/decimals
    mulPrice is eth-based chainlink price feed (1e18 decimals): the decimals defined in the contract should be 1e36
    mulPrice is usd-based chainlink price feed (1e8 decimals): the decimals defined in the contract should be 1e26
neither multiply address nor divide address is provided
price=1e36*1e18/decimals
This case will not happen as the contract has to define a chainlink price source.
```

## Decimals

Below is taken from a concern on token decimals, and documents how token decimals are expected to work within the Cog Pair Deployments.

Ok this issue seems to have been caused by a miscommunication which I take blame for, as there was confusion on the return value of the oracle. Oracles within the Cog System are expected to return a price of each token in wei to wei.

Reading through the solvency check in `cog_pair.vy`
```py
    collateral_amt: uint256 = (
        (
            collateral_share
            * (EXCHANGE_RATE_PRECISION / COLLATERIZATION_RATE_PRECISION)
        )
        * COLLATERIZATION_RATE
    )

    borrow_part = self.user_borrow_part[user]
    borrow_part = self.mul_div(
        (borrow_part * convert(_total_borrow.elastic, uint256)),
        exchange_rate,
        convert(_total_borrow.base, uint256),
        False,
    )
```

Token decimals are not accounted for, instead the exchange rate is expected to be in wei to wei, as the borrow part, in raw units is multiplied by the exchange rate, with an expected result of the value in collateral (neither collateral tokens nor asset tokens decimals are relevant here).

Additionally

[Chainlink Oracle](https://github.com/CogFinance/Cog-Finance-v1/blob/main/src/oracles/ChainlinkOracle.sol#L45) will return a price which is divided by the `decimals` of the of token for which it is providing a price, providing a price in wei, rather than tokens.

[Compound Oracle](https://github.com/CogFinance/Cog-Finance-v1/blob/main/src/oracles/CompoundOracle.sol#L70) performs a similar division by a factor of `division` which with perhaps a confusing name, divides the value of `asset/collateral` by a factor, which is expected to be any delta within the decimals of each token.

Confusingly as well when [LPChainlinkOracle](https://github.com/CogFinance/Cog-Finance-v1/blob/main/src/oracles/LPChainlinkOracle.sol#L96) fetches a price it implicitly expects this to be within wei to wei, not token unit to token unit as the rest of the units are in wei.

So the PoolSharks oracle returns the price correctly not accounting for token unit decimals, however this is poorly documented across the codebase and will be documented correctly to clearly indicated this

## Chainlink LP Token Pricing

Chainlink LP token pricing only uses eth-based price feeds, this is largely a convenience factor as most LP tokens are priced in eth. Future adjustments will likely be made, but this contract is to just handle UNI-V2 cases, and is expected to be depreciated for something able to handle concentrated liquidity pool LPs tokens after launch.