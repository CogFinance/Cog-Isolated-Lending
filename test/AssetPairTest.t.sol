// SPDX-License-Identifier: MIT
pragma solidity >=0.8.13;

import "../src/ICogPair.sol";
import "./CogPairUtil.t.sol";

contract AssetPairTest is CogPairTest {
    function test_add_asset() public {
        asset.mint(address(this), 100000);
        asset.approve(address(pair), 100000);

        pair.add_asset(address(this), 100000);
        require(asset.balanceOf(address(pair)) == 100000, "asset balance should be 100000");

        require(pair.totalSupply() == 100000, "total asset should be 100000");

        require(pair.totalSupply() == 100000, "user asset share should be 100000");
    }

    function test_remove_asset() public {
        asset.mint(address(this), 100000);
        asset.approve(address(pair), 100000);

        pair.add_asset(address(this), 100000);
        pair.remove_asset(address(this), 99000);

        require(asset.balanceOf(address(pair)) == 1000, "asset balance should be 1000 or minimum");

        require(pair.totalSupply() == 1000, "total asset should be 1000 or minimum");

        require(pair.total_asset().base == 1000, "user asset share should be 1000 or minimum");
    }

    function test_cannot_steal_asset() public {
        asset.mint(address(this), 100000);
        asset.approve(address(pair), 100000);

        pair.add_asset(address(this), 100000);
        vm.startPrank(address(0x05));
        asset.mint(address(0x05), 100000);
        asset.approve(address(pair), 100000);
        pair.add_asset(address(0x05), 100000);
        vm.stopPrank();

        vm.expectRevert();
        pair.remove_asset(address(0x123), 200000);

        require(asset.balanceOf(address(pair)) == 200000, "asset balance should be 200000");

        require(pair.totalSupply() == 200000, "total asset should be 200000");

        require(pair.balanceOf(address(0x05)) == 100000, "user asset share should be 100000");
    }

    function test_fuzz_asset(uint128 _amount0, uint128 _amount1) public {
        uint256 amount0 = _amount0;
        uint256 amount1 = _amount1;

        vm.assume(amount0 > 1000);
        vm.assume(amount1 > 1000);
        vm.assume(amount0 + amount1 < 340282366920938463463374607431768211355); // Overflow Rebase
        address depositor_0 = address(0x005);
        address depositor_1 = address(0x006);

        vm.startPrank(depositor_0);

        asset.mint(depositor_0, amount0);
        asset.approve(address(pair), amount0);
        pair.add_asset(depositor_0, amount0);

        vm.stopPrank();
        vm.startPrank(depositor_1);

        asset.mint(depositor_1, amount1);
        asset.approve(address(pair), amount1);

        pair.add_asset(depositor_1, amount1);

        require(asset.balanceOf(address(pair)) == amount0 + amount1, "asset balance should be total amount");

        require(pair.totalSupply() == amount0 + amount1, "total asset should be total amount");

        require(pair.balanceOf(depositor_0) == amount0, "user asset share should be total amount");

        require(pair.balanceOf(depositor_1) == amount1, "user asset share should be total amount");

        vm.stopPrank();
        vm.startPrank(depositor_0);

        pair.remove_asset(depositor_0, amount0);

        require(asset.balanceOf(address(pair)) == amount1, "asset balance should be 100000");

        require(pair.totalSupply() == amount1, "total asset should be 100000");
    }
}
