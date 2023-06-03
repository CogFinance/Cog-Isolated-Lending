# version 0.3.9

price: public(uint256)
updated: public(bool)


@external
def __init__():
    self.price = 0
    self.updated = False


@external
def setPrice(_price: uint256):
    self.price = _price


@external
def setUpdated(_updated: bool):
    self.updated = _updated


@view
@external
def get() -> (bool, uint256):
    return (self.updated, self.price)
