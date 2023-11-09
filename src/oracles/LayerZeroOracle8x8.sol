// SPDX-License-Identifier: MIT
pragma solidity 0.6.12;

import "../libraries//BoringMath.sol";
import "../interfaces/IOracle.sol";

// Chainlink Aggregator

interface IAggregatorxF33d {
    function latestRoundData(bytes32 feedHash)
        external
        view
        returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound);
}

contract LayerZeroOracle is IOracle {
    using BoringMath for uint256; // Keep everything in uint256

    address immutable price_feed;
    bytes32 immutable multiply;
    bytes32 immutable divide;
    uint256 immutable decimals;

    constructor(bytes32 _mul, bytes32 _div, uint256 _dec, address _price_feed) public {
        multiply = _mul;
        divide = _div;
        decimals = _dec;

        price_feed = _price_feed;
    }

    // Calculates the latest exchange rate
    // Uses both divide and multiply only for tokens not supported directly by Chainlink, for example MKR/USD
    function _get() internal view returns (uint256) {
        uint256 price = decimals;

        (, int256 mulPrice, ,,) = IAggregatorxF33d(price_feed).latestRoundData(multiply);
        require(mulPrice != 0, "Invalid mulPrice");
        price = price.mul(uint256(mulPrice));

        (, int256 divPrice, ,,) = IAggregatorxF33d(price_feed).latestRoundData(divide);
        require(divPrice != 0, "Invalid divPrice");
        price = price / uint256(divPrice);

        return price;
    }

    function getDataParameter() public view returns (bytes memory) {
        return abi.encode(multiply, divide, decimals);
    }

    // Get the latest exchange rate
    /// @inheritdoc IOracle
    function get() public override returns (bool, uint256) {
        return (true, _get());
    }

    // Check the last exchange rate without any state changes
    /// @inheritdoc IOracle
    function peek() public view override returns (bool, uint256) {
        return (true, _get());
    }

    // Check the current spot exchange rate without any state changes
    /// @inheritdoc IOracle
    function peekSpot() external view override returns (uint256 rate) {
        (, rate) = peek();
    }

    /// @inheritdoc IOracle
    function name() public view override returns (string memory) {
        return "Chainlink";
    }

    /// @inheritdoc IOracle
    function symbol() public view override returns (string memory) {
        return "LINK";
    }
}
