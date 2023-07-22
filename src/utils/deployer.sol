// SPDX-License-Identifier: MIT

pragma solidity 0.8.17;

contract Deployer {
    event Deployed(address addr);

    function deploy(bytes memory code) public {
        address addr;
        assembly {
            addr := create(0, add(code, 0x20), mload(code))
            if iszero(extcodesize(addr)) {
                revert(0, 0)
            }
        }
        emit Deployed(addr);
    }
}
