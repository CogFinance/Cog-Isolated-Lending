// SPDX-License-Identifier: MIT
pragma solidity >=0.8.13;

import "../../src/ICogPair.sol";
import "./CogPairUtil.t.sol";

contract CollateralPairTest is CogPairTest {
    function test_interest_rate_increases_linearly() public {
        oracle.setPrice(5000000000000000000);
        oracle.setUpdated(true);
        pair.get_exchange_rate();

        vm.startPrank(address(0x06));

        asset.mint(address(0x06), 1000000);
        asset.approve(address(pair), 1000000);

        pair.deposit(1000000, address(0x06));

        vm.stopPrank();
        vm.startPrank(address(0x07));

        collateral.mint(address(0x07), 90000000000);
        collateral.approve(address(pair), 90000000000);

        pair.add_collateral(address(0x07), 90000000000);

        uint64 interest_per_second_0 = pair.accrue_info().interest_per_second;

        pair.borrow(address(0x07), 810000); // Bump up to minimum utilization

        vm.stopPrank();

        vm.warp(block.timestamp + 864000); // 1 day

        pair.accrue();

        uint64 interest_per_second_1 = pair.accrue_info().interest_per_second;

        require(interest_per_second_1 > interest_per_second_0, "interest_per_second_1 > interest_per_second_0");
    }

    function test_interest_rate_decreases_linearly() public {
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
        pair.accrue();

        uint64 interest_per_second_0 = pair.accrue_info().interest_per_second;

        vm.stopPrank();

        vm.warp(block.timestamp + 864000); // 1 day

        vm.startPrank(address(0x07));

        asset.mint(address(0x07), 100000);
        asset.approve(address(pair), 100000);

        pair.repay(address(0x07), 100000);
        pair.accrue();

        uint64 interest_per_second_1 = pair.accrue_info().interest_per_second;

        vm.stopPrank();

        require(interest_per_second_1 < interest_per_second_0, "interest_per_second_1 < interest_per_second_0");
    }

    function test_interest_rate_accrues_value() public {
        oracle.setPrice(5000000000000000000);
        oracle.setUpdated(true);
        pair.get_exchange_rate();

        vm.startPrank(address(0x06));

        asset.mint(address(0x06), 10000000);
        asset.approve(address(pair), 10000000);

        pair.deposit(10000000, address(0x06));

        vm.stopPrank();
        vm.startPrank(address(0x07));

        collateral.mint(address(0x07), 90000000000);
        collateral.approve(address(pair), 90000000000);

        pair.add_collateral(address(0x07), 90000000000);

        pair.borrow(address(0x07), 810000); // Bump up to minimum utilization

        vm.stopPrank();

        vm.warp(block.timestamp + 2678400); // About one month

        pair.accrue();

        vm.startPrank(address(0x07));

        uint256 borrow_share = pair.user_borrow_part(address(0x07));
        asset.mint(address(0x07), borrow_share);
        asset.approve(address(pair), borrow_share);
        pair.repay(address(0x07), borrow_share);

        vm.stopPrank();
        vm.startPrank(address(0x06));

        pair.accrue();
        pair.withdraw(810050, address(0x06), address(0x06));
    }
}
