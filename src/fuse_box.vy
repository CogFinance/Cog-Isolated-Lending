# @version 0.3.9

"""
@title Fuse Box
@author cog.finance
@license AGPL-3.0
@notice A robust Oracle Implementation with secure upgradability in mind, and simplicity at its core.
"""

# ///////////////////////////////////////////////////// #
#               2Step Ownership Ty Snekmate             #
# ///////////////////////////////////////////////////// #

# @dev Returns the address of the current owner.
owner: public(address)


# @dev Returns the address of the pending owner.
pending_owner: public(address)


# @dev Emitted when the ownership transfer from
# `previous_owner` to `new_owner` is initiated.
event OwnershipTransferStarted:
    previous_owner: indexed(address)
    new_owner: indexed(address)


# @dev Emitted when the ownership is transferred
# from `previous_owner` to `new_owner`.
event OwnershipTransferred:
    previous_owner: indexed(address)
    new_owner: indexed(address)


@external
def transfer_ownership(new_owner: address):
    """
    @dev Starts the ownership transfer of the contract
         to a new account `new_owner`.
    @notice Note that this function can only be
            called by the current `owner`. Also, there is
            no security risk in setting `new_owner` to the
            zero address as the default value of `pending_owner`
            is in fact already the zero address and the zero
            address cannot call `accept_ownership`. Eventually,
            the function replaces the pending transfer if
            there is one.
    @param new_owner The 20-byte address of the new owner.
    """
    self._check_owner()
    self.pending_owner = new_owner
    log OwnershipTransferStarted(self.owner, new_owner)


@external
def accept_ownership():
    """
    @dev The new owner accepts the ownership transfer.
    @notice Note that this function can only be
            called by the current `pending_owner`.
    """
    assert (
        self.pending_owner == msg.sender
    ), "Ownable2Step: caller is not the new owner"
    self._transfer_ownership(msg.sender)


@external
def renounce_ownership():
    """
    @dev Sourced from {Ownable-renounce_ownership}.
    @notice See {Ownable-renounce_ownership} for
            the function docstring.
    """
    self._check_owner()
    self._transfer_ownership(empty(address))


@internal
def _check_owner():
    """
    @dev Throws if the sender is not the owner.
    """
    assert msg.sender == self.owner, "Ownable2Step: caller is not the owner"


@internal
def _transfer_ownership(new_owner: address):
    """
    @dev Transfers the ownership of the contract
         to a new account `new_owner` and deletes
         any pending owner.
    @notice This is an `internal` function without
            access restriction.
    @param new_owner The 20-byte address of the new owner.
    """
    self.pending_owner = empty(address)
    old_owner: address = self.owner
    self.owner = new_owner
    log OwnershipTransferred(old_owner, new_owner)


interface IOracle:
    def get() -> (bool, uint256): nonpayable


struct DataSource:
        active: bool
        oracle_address: address


fuse_box: public(DataSource[4])


@external
def __init__(sources: DataSource[4]):
    """
    @notice Fuse Box Constructor
    @param sources An array of data sources to be used by the Fuse Box
    """
    assert (
        sources[0].active
        or sources[1].active
        or sources[2].active
        or sources[3].active
    ), "FuseBox: All data sources are inactive"

    self._transfer_ownership(msg.sender)
    self.fuse_box = sources
    


@external
def defuse_source(source_index: uint256):
    """
    @notice Deactivates a data source
    @param source_index The index of the data source to deactivate
    """
    self._check_owner()
    self.fuse_box[source_index].active = False
    assert (
        self.fuse_box[0].active
        or self.fuse_box[1].active
        or self.fuse_box[2].active
        or self.fuse_box[3].active
    ), "FuseBox: All data sources are inactive"


@external
def activate_source(source_index: uint256):
    """
    @notice Activates a data source
    @param source_index The index of the data source to activate
    """
    self._check_owner()
    self.fuse_box[source_index].active = True
    # No need to check if all data sources are active, as this is a redundant check


@external
def get() -> (bool, uint256):
    """
    @return bool Whether or not the oracle updated
    @return uint256 the price of the asset
    """
    fuses: DataSource[4] = self.fuse_box

    avg_price: uint256 = 0
    active_oracles: uint256 = 0
    updated: bool = False

    for i in range(4):
        if fuses[i].active:
            active_oracles += 1

    if fuses[0].active:
        updated_0: bool = False
        price: uint256 = 0
        (updated_0, price) = IOracle(fuses[0].oracle_address).get()
        updated = updated or updated_0
        avg_price += (price / active_oracles) + (price % active_oracles)

    if fuses[1].active:
        updated_1: bool = False
        price: uint256 = 0
        (updated_1, price) = IOracle(fuses[1].oracle_address).get()
        updated = updated or updated_1
        avg_price += (price / active_oracles) + (price % active_oracles)

    if fuses[2].active:
        updated_2: bool = False
        price: uint256 = 0
        (updated_2, price) = IOracle(fuses[2].oracle_address).get()
        updated = updated or updated_2
        avg_price += (price / active_oracles) + (price % active_oracles)

    if fuses[3].active:
        updated_3: bool = False
        price: uint256 = 0
        (updated_3, price) = IOracle(fuses[3].oracle_address).get()
        updated = updated or updated_3
        avg_price += (price / active_oracles) + (price % active_oracles)


    return (updated, avg_price)
