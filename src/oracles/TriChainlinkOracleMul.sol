// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;


interface IAggregatorV2 {
    function latestAnswer() external view returns (int256 latestAnswer);

    function latestRoundData()
        external
        view
        returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound);
}

contract TriChainlinkOracleMul {
    address immutable multiply;
    address immutable multiply2;
    address immutable divide;
    uint256 immutable decimals;

    constructor(address _mul, address _mul2 ,address _div, uint256 _dec) {
        multiply = _mul;
        require(_div != address(0), "Invalid divide");
        multiply2 = _mul2;
        divide = _div;
        decimals = _dec;
    }

    // Calculates the latest exchange rate
    // Uses both divide and multiply only for tokens not supported directly by Chainlink, for example MKR/USD
    function _get() internal view returns (uint256) {
        uint256 price = uint256(1e48);

        if (multiply != address(0)) {
            int256 mulPrice = IAggregatorV2(multiply).latestAnswer();
            price = price * uint256(mulPrice);
            int256 mul2Price = IAggregatorV2(multiply2).latestAnswer();
            require(mul2Price != 0, "Invalid div2Price");
            price = price * uint256(mul2Price);
        } else {
            price = price * 1e18;
        }

        if (divide != address(0)) {
            int256 divPrice = IAggregatorV2(divide).latestAnswer();
            require(divPrice != 0, "Invalid divPrice");
            price = price / uint256(divPrice);
        }

        return price / decimals;
    }

    function getDataParameter() public view returns (bytes memory) {
        return abi.encode(multiply, divide, decimals);
    }

    // Get the latest exchange rate
    function get() public returns (bool, uint256) {
        return (true, _get());
    }

    // Check the last exchange rate without any state changes
    function peek() public view returns (bool, uint256) {
        return (true, _get());
    }

    // Check the current spot exchange rate without any state changes
    function peekSpot() external view returns (uint256 rate) {
        (, rate) = peek();
    }

    function name() public view returns (string memory) {
        return "Chainlink";
    }

    function symbol() public view returns (string memory) {
        return "LINK";
    }
}
