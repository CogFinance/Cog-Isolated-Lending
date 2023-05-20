// SPDX-License-Identifier: MIT
pragma solidity >=0.8.13;

interface IERC4626 {
    function asset() external view returns (address assetTokenAddress);
    function totalAssets() external view returns (uint256 totalManagedAssets);
    function convertToShares(uint256 assets) external view returns (uint256 shares);
    function convertToAssets(uint256 shares) external view returns (uint256 assets);
    function maxDeposit(address receiver) external view returns (uint256 maxAssets);
    function previewDeposit(uint256 assets) external view returns (uint256 shares);
    function deposit(uint256 assets, address receiver) external returns (uint256 shares);
    function maxMint(address receiver) external view returns (uint256 maxShares);
    function previewMint(uint256 shares) external view returns (uint256 assets);
    function mint(uint256 shares, address receiver) external returns (uint256 assets);
    function maxWithdraw(address owner) external view returns (uint256 maxAssets);
    function previewWithdraw(uint256 assets) external view returns (uint256 shares);
    function withdraw(uint256 assets, address receiver, address owner) external returns (uint256 shares);
    function maxRedeem(address owner) external view returns (uint256 maxShares);
    function previewRedeem(uint256 shares) external view returns (uint256 assets);
    function redeem(uint256 shares, address receiver, address owner) external returns (uint256 assets);
    event Deposit(address indexed caller, address indexed owner, uint256 assets, uint256 shares);
    event Withdraw(address indexed caller, address indexed receiver, address indexed owner, uint256 assets, uint256 shares);
}

interface ICogPair is IERC4626 {
    struct Rebase {
        uint128 elastic;
        uint128 base;
    }

    struct AccrueInfo {
        uint64 interest_per_second;
        uint64 last_accrued;
        uint128 fees_earned_fraction;
    }

    function oracle() external view returns (address);
    function asset() external view returns (address);
    function collateral() external view returns (address);
    function total_borrow() external view returns (Rebase memory);
    function accrue() external;
    function add_collateral(address to, uint256 amount) external;
    function remove_collateral(address to, uint256 amount) external;
    function borrow(address to, uint256 amount) external returns (uint256);
    function repay(address to, uint256 payment) external returns (uint256);
    function total_collateral_share() external view returns (uint256);
    function user_collateral_share(address user) external view returns (uint256);
    function user_borrow_part(address user) external view returns (uint256);
    function balanceOf(address user) external view returns (uint256);
    function total_asset() external view returns (Rebase memory);
    function totalSupply() external view returns (uint256);
    function get_exchange_rate() external returns (bool, uint256);
    function exchange_rate() external view returns (uint256);
    function accrue_info() external view returns (AccrueInfo memory);
    function liquidate(address user, uint256 maxBorrowParts, address to) external;
}


interface ICogFactory {
    function deploy_medium_risk_pair(address asset, address collateral, address oracle) external returns (address);
}