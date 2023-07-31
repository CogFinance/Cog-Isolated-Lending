// SPDX-License-Identifier: MIT
pragma solidity 0.8.19;

// @title Cog PoolSharks Oracle Adapter
// @notice THis contract works as an adapter to a PoolSharks TWAP Range Pool to act as price feed 
//  for Cog Pairs. `get()` is the only function used by Cog Pairs directly, all else exists primarily for UI Reasons
//
//                          ▒▒▒▒▒▒▒▒▒▒░░                  
//                     ▒▒▒▒▒▒▒▒▒▒▒▒░░                    
//        ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒░░                      
//    ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒░░                      
//  ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒          ▒▒▒▒▒▒▒▒
//▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒░░    ▒▒▒▒▒▒▒▒  
//▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒░░░░▒▒▒▒▒▒▒▒  
//▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒░░▒▒░░▒▒░░▒▒▒▒▒▒▒▒▒▒▒▒▒▒    
//  ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒░░▒▒░░▒▒░░▒▒▒▒▒▒▒▒▒▒▒▒▒▒    
//    ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██▒▒░░▒▒░░▒▒░░▒▒▒▒▒▒▒▒░░▒▒▒▒    
//        ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒░░░░░░  ░░▒▒    
//          ░░░░░░░░░░░░░░▒▒▒▒▒▒▒▒▒▒░░░░░░        ░░▒▒    
//            ▒▒▒▒░░░░░░░░░░░░▒▒▒▒▒▒                ░░    
//            ▒▒▒▒▒▒          ▒▒▒▒▒▒                      
//            ▒▒▒▒▒▒            ▒▒▒▒                      
//            ▒▒▒▒                ▒▒                      
//            ▒▒                                          


interface PoolSharksRangePool {
    function token0() external view returns (address);
    function token1() external view returns (address);

    function sample(uint32[] memory secondsAgo)
        external
        view
        returns (
            int56[] memory tickSecondsAccum,
            uint160[] memory secondsPerLiquidityAccum,
            uint160 averagePrice,
            uint128 averageLiquidity,
            int24 averageTick
        );
}

interface IOracle {
    /// @notice Get the latest exchange rate.
    /// @return success if no valid (recent) rate is available, return false else true.
    /// @return rate The rate of the requested asset / pair / pool.
    function get() external returns (bool success, uint256 rate);

    /// @notice Check the last exchange rate without any state changes.
    /// @return success if no valid (recent) rate is available, return false else true.
    /// @return rate The rate of the requested asset / pair / pool.
    function peek() external view returns (bool success, uint256 rate);

    /// @notice Check the current spot exchange rate without any state changes. For oracles like TWAP this will be different from peek().
    /// @return rate The rate of the requested asset / pair / pool.
    function peekSpot() external view returns (uint256 rate);

    /// @notice Returns a human readable (short) name about this oracle.
    /// @return (string) A human readable symbol name about this oracle.
    function symbol() external view returns (string memory);

    /// @notice Returns a human readable name about this oracle.
    /// @return (string) A human readable name about this oracle.
    function name() external view returns (string memory);
}

contract PoolSharksOracle is IOracle {
    uint256 constant PRECISION = 1e18;
    PoolSharksRangePool public immutable pool;
    address public immutable token;

    /// This is an average price based off a TWAP, and not a real-time price which should be used
    uint256 lastPrice;

    // @param poolAddress  The address of the Range pool which will act as a price information source
    // @param tokenAddress The address of the token this oracle should act as a price feed for
    constructor(address poolAddress, address tokenAddress) {
        pool = PoolSharksRangePool(poolAddress);
        token = tokenAddress;
        require(pool.token0() == tokenAddress || pool.token1() == tokenAddress, "Invalid Pair for Given Token");
    }

    // @return The updated price for token, with 18 decimals places
    function calculatePrice() internal view returns (uint256) {
        // averagePrice is token1 per token0
        uint32[] memory samples = new uint32[](3);
        samples[0] = 0;
        samples[1] = 30 seconds;
        samples[2] = 1 minutes;

        (,, uint160 averagePrice,,) = pool.sample(samples);

        uint256 normalizedPrice;

        // fullPrice is currently in Q64.96
        // so to reformat it to 1e18
        //  fullPrice    normalizedPrice
        //  --------- = ------------------
        //    2**96           1e18
        //
        // So we multiply fullPrice by 1e18 then divide by 2 ** 96
        if (averagePrice > type(uint128).max) {
            averagePrice >>= 32;
            uint256 fullPrice = mulDiv(averagePrice, averagePrice, 2 ** 64);
            // Because we have already rsh 32 bits so fullPrice is a Q.64
            normalizedPrice = mulDiv(fullPrice, 1e18, 2 ** 64);
        } else {
            uint256 fullPrice = mulDiv(averagePrice, averagePrice, 2 ** 96);
            normalizedPrice = mulDiv(fullPrice, 1e18, 2 ** 96);
        }

        if (pool.token1() == token) {
            // We are trying to get price of token0
            return (1 * normalizedPrice);
        } else {
            // We are trying to get the price of token1
            // Because 1e18 for oracle precision, we return normalizedPrice multiplied by a conversion
            // factor of 1e36 over normalizedPrice
            return (1e36 / normalizedPrice);
        }
    }

    // @return bool Updated
    // @return price The price of token with 18 decimal place
    function get() external returns (bool, uint256) {
        uint256 currentPrice = calculatePrice();
        if (currentPrice != lastPrice) {
            lastPrice = currentPrice;
            return (true, currentPrice);
        } else {
            // Cheaper than reading again from storage
            return (false, currentPrice);
        }
    }

    // @return bool Updated
    // @return price The price of token with 18 decimal place
    function peek() external view returns (bool success, uint256 rate) {
        uint256 currentPrice = calculatePrice();
        if (currentPrice != lastPrice) {
            return (true, currentPrice);
        } else {
            // Cheaper than reading again from storage
            return (false, currentPrice);
        }
    }

    // @return price The price of token with 18 decimal place
    function peekSpot() external view returns (uint256 rate) {
        rate = calculatePrice();
    }

    // @return The name of the Oracle
    function name() external pure returns (string memory) {
        return "PoolSharks LP Token Oracle";
    }
    
    // @return Symbol for the Oracle
    function symbol() external pure returns (string memory) {
        return "Pool";
    }

    /// @notice Calculates floor(a×b÷denominator) with full precision. Throws if result overflows a uint256 or denominator == 0
    /// @param a The multiplicand
    /// @param b The multiplier
    /// @param denominator The divisor
    /// @return result The 256-bit result
    /// @dev Credit to Remco Bloemen under MIT license https://xn--2-umb.com/21/muldiv
    function mulDiv(uint256 a, uint256 b, uint256 denominator) internal pure returns (uint256 result) {
        // 512-bit multiply [prod1 prod0] = a * b
        // Compute the product mod 2**256 and mod 2**256 - 1
        // then use the Chinese Remainder Theorem to reconstruct
        // the 512 bit result. The result is stored in two 256
        // variables such that product = prod1 * 2**256 + prod0
        uint256 prod0; // Least significant 256 bits of the product
        uint256 prod1; // Most significant 256 bits of the product
        assembly {
            let mm := mulmod(a, b, not(0))
            prod0 := mul(a, b)
            prod1 := sub(sub(mm, prod0), lt(mm, prod0))
        }

        // Handle non-overflow cases, 256 by 256 division
        if (prod1 == 0) {
            require(denominator > 0);
            assembly {
                result := div(prod0, denominator)
            }
            return result;
        }

        // Make sure the result is less than 2**256.
        // Also prevents denominator == 0
        require(denominator > prod1);

        ///////////////////////////////////////////////
        // 512 by 256 division.
        ///////////////////////////////////////////////

        // Make division exact by subtracting the remainder from [prod1 prod0]
        // Compute remainder using mulmod
        uint256 remainder;
        assembly {
            remainder := mulmod(a, b, denominator)
        }
        // Subtract 256 bit number from 512 bit number
        assembly {
            prod1 := sub(prod1, gt(remainder, prod0))
            prod0 := sub(prod0, remainder)
        }

        // Factor powers of two out of denominator
        // Compute largest power of two divisor of denominator.
        // Always >= 1.
        unchecked {
            uint256 twos = (type(uint256).max - denominator + 1) & denominator;
            // Divide denominator by power of two
            assembly {
                denominator := div(denominator, twos)
            }

            // Divide [prod1 prod0] by the factors of two
            assembly {
                prod0 := div(prod0, twos)
            }
            // Shift in bits from prod1 into prod0. For this we need
            // to flip `twos` such that it is 2**256 / twos.
            // If twos is zero, then it becomes one
            assembly {
                twos := add(div(sub(0, twos), twos), 1)
            }
            prod0 |= prod1 * twos;

            // Invert denominator mod 2**256
            // Now that denominator is an odd number, it has an inverse
            // modulo 2**256 such that denominator * inv = 1 mod 2**256.
            // Compute the inverse by starting with a seed that is correct
            // correct for four bits. That is, denominator * inv = 1 mod 2**4
            uint256 inv = (3 * denominator) ^ 2;
            // Now use Newton-Raphson iteration to improve the precision.
            // Thanks to Hensel's lifting lemma, this also works in modular
            // arithmetic, doubling the correct bits in each step.
            inv *= 2 - denominator * inv; // inverse mod 2**8
            inv *= 2 - denominator * inv; // inverse mod 2**16
            inv *= 2 - denominator * inv; // inverse mod 2**32
            inv *= 2 - denominator * inv; // inverse mod 2**64
            inv *= 2 - denominator * inv; // inverse mod 2**128
            inv *= 2 - denominator * inv; // inverse mod 2**256

            // Because the division is now exact we can divide by multiplying
            // with the modular inverse of denominator. This will give us the
            // correct result modulo 2**256. Since the precoditions guarantee
            // that the outcome is less than 2**256, this is the final result.
            // We don't need to compute the high bits of the result and prod1
            // is no longer required.
            result = prod0 * inv;
            return result;
        }
    }
}
