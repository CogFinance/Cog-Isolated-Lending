// SPDX-License-Identifier: MIT
pragma solidity >=0.8.13;

import "forge-std/Test.sol";
import "../../lib/utils/VyperDeployer.sol";
import "../../src/ICogPair.sol";
import "../mocks/MockERC20.sol";
import "../mocks/MockOracle.sol";

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
        asset = new MockERC20("asset", "TKA", 18);
        collateral = new MockERC20("collateral", "TKB", 18);
        oracle = new MockOracle();

        address pair_blueprint = vyperDeployer.deployBlueprint("cog_medium_pair");
        address pair_factory = vyperDeployer.deployContract("cog_factory", abi.encode(pair_blueprint));
        pair = ICogPair(ICogFactory(pair_factory).deploy_medium_risk_pair(address(asset), address(collateral), address(oracle)));
        
        vm = Vm(HEVM_ADDRESS);
    }
}
