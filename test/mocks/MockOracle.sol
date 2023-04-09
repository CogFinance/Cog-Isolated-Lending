pragma solidity >=0.8.13;

contract MockOracle {
    uint256 public price;
    bool public updated;
    uint256 dumb_warning;

    function setPrice(uint256 _price) public {
        price = _price;
    }

    function setUpdated(bool _updated) public {
        updated = _updated;
    }

    function get() external returns (bool, uint256) {
        dumb_warning = 0; // To get rid of annoying warning
        return (updated, price);
    }
}
