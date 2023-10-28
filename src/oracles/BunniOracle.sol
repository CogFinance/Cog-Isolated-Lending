// SPDX-License-Identifier: MIT
pragma solidity 0.8.19;

import "../interfaces/IOracle.sol";
import "forge-std/console.sol";

//UniswapV3Pool interface
interface IUniswapV3Pool {
    function token0() external view returns (address);
    function token1() external view returns (address);
}

interface ERC20 {
    function decimals() external view returns (uint256);
}


//BunniToken interface
interface IBunniToken {
    function pool() external view returns (IUniswapV3Pool);
    function tickLower() external view returns (int24);
    function tickUpper() external view returns (int24);
}

//BunniLens interface
interface IBunniLens {
    function pricePerFullShare(BunniKey calldata key) external view returns (uint128, uint256, uint256);
}

//BunniKey struct
struct BunniKey {
    IUniswapV3Pool pool;
    int24 tickLower;
    int24 tickUpper;
}

contract BunniOracle is IOracle {
    IBunniLens public bunni_lens;
    address public bunni_token;
    BunniKey public bunni_key;
    IOracle public asset_0_oracle;
    IOracle public asset_1_oracle;
    uint256 public decimalsAsset0;
    uint256 public decimalsAsset1;

    constructor(address _bunni_lens, address _bunni_token, address _asset_0_oracle, address _asset_1_oracle) {
        IUniswapV3Pool pool = IBunniToken(_bunni_token).pool();
        int24 tickLower = IBunniToken(_bunni_token).tickLower();
        int24 tickUpper = IBunniToken(_bunni_token).tickUpper();

        bunni_key = BunniKey(pool, tickLower, tickUpper);
        bunni_lens = IBunniLens(_bunni_lens);
        bunni_token = _bunni_token;
        asset_0_oracle = IOracle(_asset_0_oracle);
        asset_1_oracle = IOracle(_asset_1_oracle);
        decimalsAsset0 = ERC20(pool.token0()).decimals();
        decimalsAsset1 = ERC20(pool.token1()).decimals();
    }

    function _getFinalRate(uint256 rate0, uint256 rate1) internal view returns(uint256) {
        (, uint256 amount0, uint256 amount1) = bunni_lens.pricePerFullShare(bunni_key);
        return  (amount0 * rate0) / 10 ** decimalsAsset0 + (amount1 * rate1) / 10 ** decimalsAsset1;
    }

    
    function get() external returns (bool, uint256) {
        (bool success0, uint256 rate0) = asset_0_oracle.get();
        (bool success1, uint256 rate1) = asset_1_oracle.get();

        uint256 finalRate = _getFinalRate(rate0, rate1);
        return (success0 && success1, finalRate);
    }

    function peek() external view returns (bool, uint256) {
        (bool success0, uint256 rate0) = asset_0_oracle.peek();
        (bool success1, uint256 rate1) = asset_1_oracle.peek();

        uint256 finalRate = _getFinalRate(rate0, rate1);
        return (success0 && success1, finalRate);
    }

    function peekSpot() external view returns (uint256) {
        uint256 rate0 = asset_0_oracle.peekSpot();
        uint256 rate1 = asset_1_oracle.peekSpot();

        uint256 finalRate = _getFinalRate(rate0, rate1);
        return finalRate;
    }

    function symbol() public pure returns (string memory) {
        return "BUNNI";
    }

    function name() public pure returns (string memory) {
        return "Bunni";
    }
}
