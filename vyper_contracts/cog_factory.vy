# @version 0.3.7

"""
@title Cog Factory
@license GNU Affero General Public License v3.0
@author Cog Finance
@notice A privledged factory for creating Cog Pairs and managing their protocol-owned liquidity
"""

# Ty snekmate for the ownership code

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


interface ICogPair:
    def update_borrow_fee(newFee: uint256): nonpayable
    def update_default_protocol_fee(newFee: uint256): nonpayable
    def pause(): nonpayable
    def unpause(): nonpayable


event PairCreated:
    asset: indexed(address)
    collateral: indexed(address)
    pair: indexed(address)


medium_blueprint: immutable(address)

priv_users: public(HashMap[address, bool])

fee_to: public(address)


@external
def __init__(_medium_blueprint: address, fee_to: address):
    """
    Initialize the contract
    """
    medium_blueprint = _medium_blueprint
    self.fee_to = fee_to
    self._transfer_ownership(msg.sender)


@external
def deploy_medium_risk_pair(
    asset: address, collateral: address, oracle: address
) -> address:
    """
    Deploy a medium risk pair
    """
    pair: address = create_from_blueprint(
        medium_blueprint, asset, collateral, oracle, code_offset=3
    )
    log PairCreated(asset, collateral, pair)
    return pair


@external
def setPrivUserStatus(user: address, status: bool):
    self._check_owner()
    self.priv_users[user] = status


@external
def update_borrow_fee(pair: address, newFee: uint256):
    self._check_owner()
    ICogPair(pair).update_borrow_fee(newFee)


@external
def update_default_protocol_fee(pair: address, newFee: uint256):
    self._check_owner()
    ICogPair(pair).update_default_protocol_fee(newFee)


@external
def change_fee_to(new_owner: address):
    """
    @dev Returns the address to which protocol fees arema sent.
    """
    self._check_owner()
    self.fee_to = new_owner


@external
def pause(pair: address):
    assert (self.priv_users[msg.sender] == True)
    ICogPair(pair).pause()


@external
def unpause(pair: address):
    assert (self.priv_users[msg.sender] == True)
    ICogPair(pair).unpause()
