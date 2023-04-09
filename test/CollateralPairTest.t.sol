// SPDX-License-Identifier: MIT
pragma solidity >=0.8.13;

import "../src/ICogPair.sol";
import "./CogPairUtil.t.sol";

contract CollateralPairTest is CogPairTest {
    function test_add_collateral() public {
        collateral.mint(address(this), 100000);
        collateral.approve(address(pair), 100000);

        pair.add_collateral(address(this), 100000);
        require(collateral.balanceOf(address(pair)) == 100000, "collateral balance should be 100000");

        require(pair.total_collateral_share() == 100000, "total collateral should be 100000");

        require(pair.user_collateral_share(address(this)) == 100000, "user collateral share should be 100000");
    }

    function test_remove_collateral() public {
        collateral.mint(address(this), 100000);
        collateral.approve(address(pair), 100000);

        pair.add_collateral(address(this), 100000);
        pair.remove_collateral(address(this), 100000);

        require(collateral.balanceOf(address(pair)) == 0, "collateral balance should be 0");

        require(pair.total_collateral_share() == 0, "total collateral should be 0");

        require(pair.user_collateral_share(address(this)) == 0, "user collateral share should be 0");
    }

    function test_cannot_steal_collateral() public {
        collateral.mint(address(this), 100000);
        collateral.approve(address(pair), 100000);

        pair.add_collateral(address(this), 100000);
        vm.startPrank(address(0x05));
        collateral.mint(address(0x05), 100000);
        collateral.approve(address(pair), 100000);
        pair.add_collateral(address(0x05), 100000);
        vm.stopPrank();

        vm.expectRevert();
        pair.remove_collateral(address(0x123), 200000);

        require(collateral.balanceOf(address(pair)) == 200000, "collateral balance should be 200000");

        require(pair.total_collateral_share() == 200000, "total collateral should be 200000");

        require(pair.user_collateral_share(address(this)) == 100000, "user collateral share should be 100000");
    }

    function test_fuzz_collateral(uint128 _amount0, uint128 _amount1) public {
        uint256 amount0 = _amount0;
        uint256 amount1 = _amount1;

        vm.assume(amount0 > 1000);
        vm.assume(amount1 > 1000);
        vm.assume(amount0 + amount1 < 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff);
        address depositor_0 = address(0x005);
        address depositor_1 = address(0x006);

        vm.startPrank(depositor_0);

        collateral.mint(depositor_0, amount0);
        collateral.approve(address(pair), amount0);
        pair.add_collateral(depositor_0, amount0);
        vm.stopPrank();
        vm.startPrank(depositor_1);

        collateral.mint(depositor_1, amount1);
        collateral.approve(address(pair), amount1);

        pair.add_collateral(depositor_1, amount1);

        require(collateral.balanceOf(address(pair)) == amount0 + amount1, "collateral balance should be total amount");

        require(pair.total_collateral_share() == amount0 + amount1, "total collateral should be total amount");

        require(pair.user_collateral_share(depositor_0) == amount0, "user collateral share should be total amount");

        require(pair.user_collateral_share(depositor_1) == amount1, "user collateral share should be total amount");

        vm.stopPrank();
        vm.startPrank(depositor_0);

        pair.remove_collateral(depositor_0, amount0);

        require(collateral.balanceOf(address(pair)) == amount1, "collateral balance should be 100000");

        require(pair.total_collateral_share() == amount1, "total collateral should be 100000");
    }
}
