// SPDX-License-Identifier: MIT
pragma solidity 0.6.12;

import "../libraries/BoringMath.sol";
import "../interfaces/IOracle.sol";

interface IUniswapAnchoredView {
    function price(string memory symbol) external view returns (uint256);
}

contract CompoundOracle is IOracle {
    using BoringMath for uint256;

    IUniswapAnchoredView private constant ORACLE = IUniswapAnchoredView(0x922018674c12a7F0D394ebEEf9B58F186CdE13c1);

    struct PriceInfo {
        uint128 price;
        uint128 blockNumber;
    }

    mapping(string => PriceInfo) public prices;

    string public collateralSymbol;
    string public assetSymbol;
    uint256 public immutable division;

    constructor(string memory _collateralSymbol, string memory _assetSymbol, uint256 div) public {
        collateralSymbol = _collateralSymbol;
        assetSymbol = _assetSymbol;
        division = div;
    }

    function _peekPrice(string memory symbol) internal view returns (uint256) {
        if (bytes(symbol).length == 0) {
            return 1000000;
        } // To allow only using collateralSymbol or assetSymbol if paired against USDx
        PriceInfo memory info = prices[symbol];
        if (block.number > info.blockNumber + 8) {
            return uint128(ORACLE.price(symbol)); // Prices are denominated with 6 decimals, so will fit in uint128
        }
        return info.price;
    }

    function _getPrice(string memory symbol) internal returns (uint256) {
        if (bytes(symbol).length == 0) {
            return 1000000;
        } // To allow only using collateralSymbol or assetSymbol if paired against USDx
        PriceInfo memory info = prices[symbol];
        if (block.number > info.blockNumber + 8) {
            info.price = uint128(ORACLE.price(symbol)); // Prices are denominated with 6 decimals, so will fit in uint128
            info.blockNumber = uint128(block.number); // Blocknumber will fit in uint128
            prices[symbol] = info;
        }
        return info.price;
    }

    function getDataParameter(string memory collateralSymbol, string memory assetSymbol, uint256 division)
        public
        pure
        returns (bytes memory)
    {
        return abi.encode(collateralSymbol, assetSymbol, division);
    }

    // Get the latest exchange rate
    /// @inheritdoc IOracle
    function get() public override returns (bool, uint256) {
        return (true, uint256(1e36).mul(_getPrice(assetSymbol)) / _getPrice(collateralSymbol) / division);
    }

    // Check the last exchange rate without any state changes
    /// @inheritdoc IOracle
    function peek() public view override returns (bool, uint256) {
        return (true, uint256(1e36).mul(_peekPrice(assetSymbol)) / _peekPrice(collateralSymbol) / division);
    }

    // Check the current spot exchange rate without any state changes
    /// @inheritdoc IOracle
    function peekSpot() external view override returns (uint256 rate) {
        (, rate) = peek();
    }

    /// @inheritdoc IOracle
    function name() public view override returns (string memory) {
        return "Compound";
    }

    /// @inheritdoc IOracle
    function symbol() public view override returns (string memory) {
        return "COMP";
    }
}
