# @version 0.3.7
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
    assert self.pending_owner == msg.sender, "Ownable2Step: caller is not the new owner"
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

enum OracleType:
    UNISWAP
    POOLSHARKS
    CHAINLINK

struct DataSource:
    active: bool
    oracle_type: OracleType
    weight: uint16
    oracle_address: address

# 5 Minute interval
twap_interval: constant(uint32) = 300000
fuse_box: public(DataSource[4])

@external
def __init__(sources: DataSource[4]):
    """
    @notice Fuse Box Constructor
    @param sources An array of data sources to be used by the Fuse Box
    """
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
    assert self.fuse_box[0].active or self.fuse_box[1].active or self.fuse_box[2].active or self.fuse_box[3].active, "FuseBox: All data sources are inactive"

@external
def activate_source(source_index: uint256):
    """
    @notice Activates a data source
    @param source_index The index of the data source to activate
    """
    self._check_owner()
    self.fuse_box[source_index].active = True
    # No need to check if all data sources are active, as this is a redundant check

@internal
def get_sqrt_ratio_at_tick(tick: int24) -> uint160:
    """
    @notice A Port of the UniswapV3 TickMath getSqrtRatioAtTick
    @param tick The tick of the pool

    @return The price of the pool at the given tick, in token1/token0
    """
    abs_tick: uint256 = 0
    if tick < 0:
        abs_tick = convert(convert(-tick, int256), uint256)
    else:
        abs_tick = convert(tick, uint256)

    assert abs_tick <= 887272, "T"

    ratio: uint256 = 0
    if abs_tick & convert(0x01, uint256) != 0:
        ratio = convert(0xfffcb933bd6fad37aa2d162d1a594001, uint256)
    else:
        ratio = convert(0x0100000000000000000000000000000000, uint256)

    if abs_tick & convert(0x02, uint256) != 0:
        ratio = shift((ratio * convert(0xfff97272373d413259a46990580e213a, uint256)) , -128)
    if abs_tick & convert(0x04, uint256) != 0:
        ratio = shift((ratio * convert(0xfff2e50f5f656932ef12357cf3c7fdcc, uint256)) , -128)
    if abs_tick & convert(0x08, uint256) != 0:
        ratio = shift((ratio * convert(0xffe5caca7e10e4e61c3624eaa0941cd0, uint256)) , -128)
    if abs_tick & convert(0x10, uint256) != 0:
        ratio = shift((ratio * convert(0xffcb9843d60f6159c9db58835c926644, uint256)) , -128)
    if abs_tick & convert(0x20, uint256) != 0:
        ratio = shift((ratio * convert(0xff973b41fa98c081472e6896dfb254c0, uint256)) , -128)
    if abs_tick & convert(0x40, uint256) != 0:
        ratio = shift((ratio * convert(0xff2ea16466c96a3843ec78b326b52861, uint256)) , -128)
    if abs_tick & convert(0x80, uint256) != 0:
        ratio = shift((ratio * convert(0xfe5dee046a99a2a811c461f1969c3053, uint256)) , -128)
    if abs_tick & convert(0x0100, uint256) != 0:
        ratio = shift((ratio * convert(0xfcbe86c7900a88aedcffc83b479aa3a4, uint256)) , -128)
    if abs_tick & convert(0x0200, uint256) != 0:
        ratio = shift((ratio * convert(0xf987a7253ac413176f2b074cf7815e54, uint256)) , -128)
    if abs_tick & convert(0x0400, uint256) != 0:
        ratio = shift((ratio * convert(0xf3392b0822b70005940c7a398e4b70f3, uint256)) , -128)
    if abs_tick & convert(0x0800, uint256) != 0:
        ratio = shift((ratio * convert(0xe7159475a2c29b7443b29c7fa6e889d9, uint256)) , -128)
    if abs_tick & convert(0x1000, uint256) != 0:
        ratio = shift((ratio * convert(0xd097f3bdfd2022b8845ad8f792aa5825, uint256)) , -128)
    if abs_tick & convert(0x2000, uint256) != 0:
        ratio = shift((ratio * convert(0xa9f746462d870fdf8a65dc1f90e061e5, uint256)) , -128)
    if abs_tick & convert(0x4000, uint256) != 0:
        ratio = shift((ratio * convert(0x70d869a156d2a1b890bb3df62baf32f7, uint256)) , -128)
    if abs_tick & convert(0x8000, uint256) != 0:
        ratio = shift((ratio * convert(0x31be135f97d08fd981231505542fcfa6, uint256)) , -128)
    if abs_tick & convert(0x010000, uint256) != 0:
        ratio = shift((ratio * convert(0x09aa508b5b7a84e1c677de54f3e99bc9, uint256)) , -128)
    if abs_tick & convert(0x020000, uint256) != 0:
        ratio = shift((ratio * convert(0x5d6af8dedb81196699c329225ee604, uint256)) , -128)
    if abs_tick & convert(0x040000, uint256) != 0:
        ratio = shift((ratio * convert(0x2216e584f5fa1ea926041bedfe98, uint256)) , -128)
    if abs_tick & convert(0x080000, uint256) != 0:
        ratio = shift((ratio * convert(0x048a170391f7dc42444e8fa2, uint256)) , -128)

    if tick > 0:
        ratio = max_value(uint256) / ratio
    
    sqrtPriceX96: uint160 = 0
    if (ratio % (shift(1, 32))) == 0:
        sqrtPriceX96 = convert(shift(ratio , -32), uint160)
    else:
        sqrtPriceX96 = convert(((shift(ratio , -32)) + 1), uint160)

    return sqrtPriceX96



interface UniswapV3Pool:
    # int56[] memory tickCumulatives, uint160[] memory secondsPerLiquidityCumulativeX128s
    def observe(secondsAgos: uint32[2]) -> (int56[2], uint160[2]): view

@internal
def fetch_uniswap_twap(oracle: address) -> uint256:

     #           uint32[] memory secondsAgos = new uint32[](2);
    #        secondsAgos[0] = twapInterval; // from (before)
    #        secondsAgos[1] = 0; // to (now)

     #       (int56[] memory tickCumulatives, ) = IUniswapV3Pool(uniswapV3Pool).observe(secondsAgos);

    #        // tick(imprecise as it's an integer) to price
    #        sqrtPriceX96 = TickMath.getSqrtRatioAtTick(
    #            int24((tickCumulatives[1] - tickCumulatives[0]) / twapInterval)
    #        );
    seconds_ago: uint32[2] = [twap_interval, 0]

    tick_cumulatives: int56[2] = [0, 0]
    seconds_per_liquidity_cumulative_x128s: uint160[2] = [0, 0]

    tick_cumulatives, seconds_per_liquidity_cumulative_x128s  = UniswapV3Pool(oracle).observe(seconds_ago)





    return 0