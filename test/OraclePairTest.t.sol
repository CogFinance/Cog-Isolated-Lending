// SPDX-License-Identifier: MIT
pragma solidity >=0.8.13;

import "../src/ICogPair.sol";
import "./CogPairUtil.t.sol";

contract CollateralPairTest is CogPairTest {
    function test_oracle_setup() public {
        (bool updated, uint256 price) = pair.get_exchange_rate();

        require(updated == false, "oracle should not be updated");
        require(price == 0, "price should be 0");

        oracle.setPrice(1000000000000000000);
        oracle.setUpdated(true);

        (updated, price) = pair.get_exchange_rate();

        require(updated == true, "oracle should be updated");
        require(price == 1000000000000000000, "price should be 1");
    }
}
