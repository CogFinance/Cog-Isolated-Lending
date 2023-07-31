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
}

contract PoolSharksOracleTest is Test {
  PoolSharksOracle oracle;
  IERC20 tokenA;
  IERC20 tokenB;


  function setUp() public {
  }

  function test_get() public {
    uint256 scrollForkId = vm.createFork("https://alpha-rpc.scroll.io/l2");
    vm.selectFork(scrollForkId);
    //vm.rollFork(4_340_000);
    tokenA = IERC20(0x895e1c476130cE9e1b19E01be8801f19122a958C);
    tokenB = IERC20(0x58d8235108E12E6B725A53B57CD0b00C5eDeE0da);
    // Pool Address
    oracle = new PoolSharksOracle(0xe4FCFFC96143b0B4b4c771432A85B969a9267D45, address(tokenA));
    oracle.get();
  }
}
