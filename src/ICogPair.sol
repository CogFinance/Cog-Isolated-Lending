// SPDX-License-Identifier: MIT
pragma solidity >=0.8.13;

interface ICogPair {
    struct Rebase {
        uint128 elastic;
        uint128 base;
    }

    struct AccrueInfo {
        uint64 interest_per_second;
        uint64 last_accrued;
        uint128 fees_earned_fraction;
    }

    function accrue() external;
    function add_collateral(address to, uint256 amount) external;
    function remove_collateral(address to, uint256 amount) external;
    function add_asset(address to, uint256 amount) external returns (uint256);
    function remove_asset(address to, uint256 amount) external returns (uint256);
    function borrow(address to, uint256 amount) external returns (uint256);
    function repay(address to, uint256 payment) external returns (uint256);
    function setup(address token_a, address token_b, address oracle) external;
    function total_collateral_share() external view returns (uint256);
    function user_collateral_share(address user) external view returns (uint256);
    function user_borrow_part(address user) external view returns (uint256);
    function balanceOf(address user) external view returns (uint256);
    function total_asset() external view returns (Rebase memory);
    function totalSupply() external view returns (uint256);
    function get_exchange_rate() external returns (bool, uint256);
    function exchange_rate() external view returns (uint256);
    function accrue_info() external view returns (AccrueInfo memory);
}
