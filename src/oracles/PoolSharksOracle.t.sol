pragma solidity 0.8.19;

import "./PoolSharksOracle.sol";
import { Vm } from "forge-std/Vm.sol";
import { Test } from "forge-std/Test.sol";

interface IERC20 {
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
    function totalSupply() external view returns (uint256);
    function balanceOf(address account) external view returns (uint256);
    function transfer(address to, uint256 value) external returns (bool);
    function allowance(address owner, address spender) external view returns (uint256);
    function approve(address spender, uint256 value) external returns (bool);
    function transferFrom(address from, address to, uint256 value) external returns (bool);
    function mint(address to, uint256 amount) external;
}

interface PoolSharksRouter {
  struct SwapParams {
    address to;
    uint160 priceLimit;
    uint128  amount;
    bool exactIn;
    bool zeroForOne;
    bytes callbackData;
  }

  function multiCall(
    address[] memory pools,
    SwapParams[] memory params 
  ) external;
}

contract PoolSharksOracleTest is Test {
  PoolSharksOracle oracleA;
  PoolSharksOracle oracleB;

  IERC20 tokenA;
  IERC20 tokenB;

  PoolSharksRouter router;

  function setUp() public {
    uint256 scrollForkId = vm.createFork("https://alpha-rpc.scroll.io/l2");
    vm.selectFork(scrollForkId);
    vm.rollFork(4_358_100);

    tokenA = IERC20(0x51C65a3D7fb6304206b64888DAF95285374F3a96);
    tokenB = IERC20(0xaC424407A8BBaA42A781Eb94F83AE37231594A4a);

    router = PoolSharksRouter(0xfaF9ea467dCb1581c66939A2781bBBBae0B2E615);

    // Pool Address
    oracleA = new PoolSharksOracle(0xbe73f88E14f172a35b107b9D893c6721990dbd81, address(tokenA));
    oracleB = new PoolSharksOracle(0xbe73f88E14f172a35b107b9D893c6721990dbd81, address(tokenB));
  }

  function test_get_oracle_B() public {
    (bool updated_0, uint256 price_0) = oracleB.get();

    // Price should be updated the first time the oracle is called
    assertEq(updated_0, true);

    // Price has not changed, so oracle is not updated
    (bool updated_1, uint256 price_1) = oracleB.get();
    assertEq(updated_1, false);
    assertEq(price_1, price_0);

    // Price is about 5 in the pool, and will see some variance due to precision
    // expected precision loss, but this should only only undervalue the collateral, which
    // benefits the lenders, not the borrowers, thus err'ing on the side of caution
    assertApproxEqAbs(price_0, 5e18, 1e14);

    bytes memory data;

    PoolSharksRouter.SwapParams memory params = PoolSharksRouter.SwapParams({
      to: address(this),
      priceLimit: type(uint160).max,
      amount: 100e18,
      exactIn: true,
      zeroForOne: false,
      callbackData: data
    });

    address[] memory pools = new address[](1);
    pools[0] = 0xbe73f88E14f172a35b107b9D893c6721990dbd81; 

    PoolSharksRouter.SwapParams[] memory swapParams = new PoolSharksRouter.SwapParams[](1);
    swapParams[0] = params;

    tokenB.mint(address(this), 100e18);
    tokenB.approve(address(router), 100e18);
    router.multiCall(pools, swapParams);

    vm.warp(block.timestamp + 86400);
    
    tokenB.mint(address(this), 100e18);
    tokenB.approve(address(router), 100e18);
    router.multiCall(pools, swapParams);
    
    (bool updated_2, uint256 price_2) = oracleB.get();

    // Price should be updated the first time the oracle is called
    assertEq(updated_2, true);
    assert(price_2 != price_0);
  }
  
  function test_get_oracle_A() public {
    (bool updated_0, uint256 price_0) = oracleA.get();

    // Price should be updated the first time the oracle is called
    assertEq(updated_0, true);

    // Price has not changed, so oracle is not updated
    (bool updated_1, uint256 price_1) = oracleA.get();
    assertEq(updated_1, false);
    assertEq(price_1, price_0);

    // Price of token A in relation to tokenB is about 0.2
    assertApproxEqAbs(price_0, 0.2e18, 1e14);

    bytes memory data;

    PoolSharksRouter.SwapParams memory params = PoolSharksRouter.SwapParams({
      to: address(this),
      priceLimit: type(uint160).max,
      amount: 100e18,
      exactIn: true,
      zeroForOne: false,
      callbackData: data
    });

    address[] memory pools = new address[](1);
    pools[0] = 0xbe73f88E14f172a35b107b9D893c6721990dbd81; 

    PoolSharksRouter.SwapParams[] memory swapParams = new PoolSharksRouter.SwapParams[](1);
    swapParams[0] = params;

    tokenB.mint(address(this), 100e18);
    tokenB.approve(address(router), 100e18);
    router.multiCall(pools, swapParams);

    vm.warp(block.timestamp + 86400);
    
    tokenB.mint(address(this), 100e18);
    tokenB.approve(address(router), 100e18);
    router.multiCall(pools, swapParams);
    
    (bool updated_2, uint256 price_2) = oracleA.get();

    // Price should be updated the first time the oracle is called
    assertEq(updated_2, true);
    assert(price_2 != price_0);
  }
}
