// SPDX-License-Identifier: MIT
pragma solidity 0.6.12;

interface IOracle {
    /// @notice Get the latest exchange rate.
    /// @return success if no valid (recent) rate is available, return false else true.
    /// @return rate The rate of the requested asset / pair / pool.
    function get() external returns (bool success, uint256 rate);

    /// @notice Check the last exchange rate without any state changes.
    /// @return success if no valid (recent) rate is available, return false else true.
    /// @return rate The rate of the requested asset / pair / pool.
    function peek() external view returns (bool success, uint256 rate);

    /// @notice Check the current spot exchange rate without any state changes. For oracles like TWAP this will be different from peek().
    /// @return rate The rate of the requested asset / pair / pool.
    function peekSpot() external view returns (uint256 rate);

    /// @notice Returns a human readable (short) name about this oracle.
    /// @return (string) A human readable symbol name about this oracle.
    function symbol() external view returns (string memory);

    /// @notice Returns a human readable name about this oracle.
    /// @return (string) A human readable name about this oracle.
    function name() external view returns (string memory);
}
