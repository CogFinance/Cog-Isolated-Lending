// SPDX-License-Identifier: MIT
pragma solidity >=0.8.13;

import "../../src/ICogPair.sol";
import "./CogPairUtil.t.sol";

contract CollateralPairTest is CogPairTest {
    function test_cannot_liquidate() public {
        oracle.setPrice(5000000000000000000);
        oracle.setUpdated(true);
        pair.get_exchange_rate();

        require(
            pair.exchange_rate() == 5000000000000000000,
            "Price should be set"
        );

        vm.startPrank(address(0x06));

        asset.mint(address(0x06), 90000000000000000000000000000);
        asset.approve(address(pair), 90000000000000000000000000000);

        pair.deposit(90000000000000000000000000000, address(0x06));

        vm.stopPrank();
        vm.startPrank(address(0x07));

        collateral.mint(address(0x07), 90000000000000000000000000000);
        collateral.approve(address(pair), 90000000000000000000000000000);

        pair.add_collateral(address(0x07), 90000000000000000000000000000);

        pair.borrow(address(0x07), 1340000000000000000000000000);

        require(
            asset.balanceOf(address(0x07)) == 1340000000000000000000000000,
            "asset balance should be 1000000"
        );

        vm.stopPrank();

        pair.accrue();

        vm.startPrank(address(0x06));
        asset.mint(address(0x06), 90000000000000000000000000000);
        asset.approve(address(pair), 90000000000000000000000000000);

        vm.expectRevert();

        pair.liquidate(
            address(0x07),
            157563025210084033613445378,
            address(0x06)
        );

        vm.stopPrank();
    }

    function test_liquidation() public {
        oracle.setPrice(5000000000000000000);
        oracle.setUpdated(true);
        pair.get_exchange_rate();

        require(
            pair.exchange_rate() == 5000000000000000000,
            "Price should be set"
        );

        vm.startPrank(address(0x06));

        asset.mint(address(0x06), 90000000000000000000000000000);
        asset.approve(address(pair), 90000000000000000000000000000);

        pair.deposit(90000000000000000000000000000, address(0x06));

        vm.stopPrank();
        vm.startPrank(address(0x07));

        collateral.mint(address(0x07), 90000000000000000000000000000);
        collateral.approve(address(pair), 90000000000000000000000000000);

        pair.add_collateral(address(0x07), 90000000000000000000000000000);

        pair.borrow(address(0x07), 1340000000000000000000000000);

        require(
            asset.balanceOf(address(0x07)) == 1340000000000000000000000000,
            "asset balance should be 1000000"
        );

        vm.stopPrank();

        oracle.setPrice(510000000000000000000);
        oracle.setUpdated(true);
        pair.get_exchange_rate();

        pair.accrue();

        vm.startPrank(address(0x06));
        asset.mint(address(0x06), 90000000000000000000000000000);
        asset.approve(address(pair), 90000000000000000000000000000);

        pair.liquidate(
            address(0x07),
            157563025210084033613445378,
            address(0x06)
        );
        vm.stopPrank();
    }
}
