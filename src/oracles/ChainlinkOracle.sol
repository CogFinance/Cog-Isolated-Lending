// SPDX-License-Identifier: MIT
pragma solidity 0.6.12;
import "../libraries/BoringMath.sol";
import "../interfaces/IOracle.sol";

// Chainlink Aggregator

interface IAggregator {
    function latestRoundData()
        external
        view
        returns (
            uint80 roundId,
            int256 answer,
            uint256 startedAt,
            uint256 updatedAt,
            uint80 answeredInRound
        );
}

contract ChainlinkOracle is IOracle {
    using BoringMath for uint256; // Keep everything in uint256

    address immutable multiply;
    address immutable divide;
    uint256 immutable decimals;

    constructor(address _mul, address _div, uint256 _dec) public {
        multiply = _mul;
        divide = _div;
        decimals = _dec;
    }

    // Calculates the lastest exchange rate
    // Uses both divide and multiply only for tokens not supported directly by Chainlink, for example MKR/USD
    function _get(
        address multiply,
        address divide,
        uint256 decimals
    ) internal view returns (uint256) {
        uint256 price = uint256(1e36);
        if (multiply != address(0)) {
            (, int256 mulPrice, , ,) = IAggregator(multiply).latestRoundData();
            price = price.mul(uint256(mulPrice));
        } else {
            price = price.mul(1e18);
        }

        if (divide != address(0)) {
            (, int256 divPrice, , ,) = IAggregator(divide).latestRoundData();
            price = price / uint256(divPrice);
        }

        return price / decimals;
    }

    function getDataParameter(
        address multiply,
        address divide,
        uint256 decimals
    ) public pure returns (bytes memory) {
        return abi.encode(multiply, divide, decimals);
    }

    // Get the latest exchange rate
    /// @inheritdoc IOracle
    function get() public override returns (bool, uint256) {
        return (true, _get(multiply, divide, decimals));
    }

    // Check the last exchange rate without any state changes
    /// @inheritdoc IOracle
    function peek() public view override returns (bool, uint256) {
        return (true, _get(multiply, divide, decimals));
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
