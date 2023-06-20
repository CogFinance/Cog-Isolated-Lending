# version 0.3.9

@view
@external
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