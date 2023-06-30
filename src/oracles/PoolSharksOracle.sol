// SPDX-License-Identifier: MIT
pragma solidity 0.8.19;

import "../interfaces/IOracle.sol";

interface PoolSharksRangePool {
    function sample(
        uint32[] memory secondsAgo
    ) external view returns (
        int56[]   memory tickSecondsAccum,
        uint160[] memory secondsPerLiquidityAccum,
        uint160 averagePrice,
        uint128 averageLiquidity,
        int24 averageTick
    );

    function token1() returns (address);

    function token0() returns (address);
}

contract PoolSharksOracle is IOracle {
  uint256 constant PRECISION = 1e18; 
  PoolSharksRangePool immutable public pool;
  address immutable public token;

  constructor(address poolAddress, address tokenAddress) external {
    pool = PoolSharksRangePool(poolAddress);
    token = tokenAddress;
    require(pool.token0() == tokenAddress || pool.token1() == tokenAddress, "Invalid Pair for Given Token");
  } 

  function calculatePrice() internal returns (bool, uint256) {
    // averagePrice is token1 per token0
    (,,uint160 averagePrice,,,) = pool.sample([0, 30 seconds]);
    bool potentialOverflow = averagePrice > type(uint128).max;

    if (potentialOverflow) {
      averagePrice >>= 32;
    }
    uint256 fullPrice = averagePrice * averagePrice;
    // fullPrice is currently in Q64.96
    // so to reformat it to 1e18
    //  fullPrice    normalizedPrice
    //  --------- = ------------------
    //    2**96           1e18
    //
    // So we multiply fullPrice by 1e18 then divide by 2 ** 96
    uint256 normalizedPrice;
    if (potentialOverflow ) {
      // Because we have already rsh 32 bits so fullPrice is a Q.64
      normalizedPrice = fullPrice.mulDiv(1e18, 2**64);
    } else {
      normalizedPrice = fullPrice.mulDiv(1e18, 2**96);
    }
    if (pool.token1() == token) {
      // We are trying to get price of token0
      return (true, 1 * normalizedPrice);
    } else {
      // We are trying to get the price of token1
      return (true, 1e36 / normalizedPrice);
    }
  }

  // @return bool Updated
  // @return price The price of token
  function get() returns (bool, uint256) {
    return calculatePrice();
  }

  function peek() returns (bool success, uint256 rate) {
    return calculatePrice();
  }

  function peekSpot() returns (uint256 rate) {
    (, rate) = calculatePrice();
  }

  function name() external view returns (string memory) {
    return "PoolSharks LP Token Oracle";
  }

  function symbol() external view returns (string memory) {
    return "Pool";
  }
}
