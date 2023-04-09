// SPDX-License-Identifier: MIT
pragma solidity >=0.8.13;

import "forge-std/Test.sol";
import "../lib/utils/VyperDeployer.sol";
import "../src/ICogPair.sol";
import "./mocks/MockERC20.sol";
import "./mocks/MockOracle.sol";

/// @title Base Contract for running CogPair Tests
contract CogPairTest is DSTest {
    ///@notice create a new instance of VyperDeployer
    VyperDeployer vyperDeployer = new VyperDeployer();

    ICogPair pair;
    MockERC20 asset;
    MockERC20 collateral;
    MockOracle oracle;
    Vm vm;

    function setUp() public {
        ///@notice deploy a new instance of ICogPair by passing in the address of the deployed Vyper contract
        pair = ICogPair(vyperDeployer.deployContract("cog_pair", abi.encode(1234)));

        asset = new MockERC20("asset", "TKA", 18);
        collateral = new MockERC20("collateral", "TKB", 18);
        oracle = new MockOracle();

        pair.setup(address(asset), address(collateral), address(oracle));

        vm = Vm(HEVM_ADDRESS);
    }
}
