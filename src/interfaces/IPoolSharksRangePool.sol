interface PoolSharksRangePool {
    function token0() external view returns (address);

    function token1() external view returns (address);

    function sample(
        uint32[] memory secondsAgo
    )
        external
        view
        returns (
            int56[] memory tickSecondsAccum,
            uint160[] memory secondsPerLiquidityAccum,
            uint160 averagePrice,
            uint128 averageLiquidity,
            int24 averageTick
        );
}
