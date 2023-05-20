// SPDX-License-Identifier: MIT
pragma solidity >=0.8.13;

import "../../src/ICogPair.sol";
import "./CogPairUtil.t.sol";

contract CollateralPairTest is CogPairTest {
    function test_borrow() public {
        oracle.setPrice(5000000000000000000);
        oracle.setUpdated(true);
        pair.get_exchange_rate();

        vm.startPrank(address(0x06));

        asset.mint(address(0x06), 90000000000000000000000000000);
        asset.approve(address(pair), 90000000000000000000000000000);

        pair.deposit(90000000000000000000000000000, address(0x06));

        vm.stopPrank();
        vm.startPrank(address(0x07));

        collateral.mint(address(0x07), 90000000000000000000000000000);
        collateral.approve(address(pair), 90000000000000000000000000000);

        pair.add_collateral(address(0x07), 90000000000000000000000000000);

        pair.borrow(address(0x07), 1000000);

        vm.stopPrank();

        require(asset.balanceOf(address(0x07)) == 1000000, "asset balance should be 1000000");

        require(pair.user_borrow_part(address(0x07)) == 1000500, "user borrow part should be 1000500, including fee");
    }

    function test_can_borrow_maximum_allowed() public {
        oracle.setPrice(1000000000000000000);
        oracle.setUpdated(true);
        pair.get_exchange_rate();

        vm.startPrank(address(0x06));

        asset.mint(address(0x06), 90000000000000000000000000000);
        asset.approve(address(pair), 90000000000000000000000000000);

        pair.deposit(90000000000000000000000000000, address(0x06));

        vm.stopPrank();
        vm.startPrank(address(0x07));

        collateral.mint(address(0x07), 1000000000000000000);
        collateral.approve(address(pair), 1000000000000000000);

        pair.add_collateral(address(0x07), 1000000000000000000);

        pair.borrow(address(0x07), 740000000000000000);

        vm.stopPrank();
    }

    function test_cannot_borrow_more_than_allowed() public {
        oracle.setPrice(1000000000000000000);
        oracle.setUpdated(true);
        pair.get_exchange_rate();

        vm.startPrank(address(0x06));

        asset.mint(address(0x06), 90000000000000000000000000000);
        asset.approve(address(pair), 90000000000000000000000000000);

        pair.deposit(90000000000000000000000000000, address(0x06));

        vm.stopPrank();
        vm.startPrank(address(0x07));

        collateral.mint(address(0x07), 1000000000000000000);
        collateral.approve(address(pair), 1000000000000000000);

        pair.add_collateral(address(0x07), 1000000000000000000);

        vm.expectRevert();
        pair.borrow(address(0x07), 750000000000000000);

        vm.stopPrank();
    }
}
