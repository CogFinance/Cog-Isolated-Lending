import ape
import pytest

from datetime import timedelta

from hypothesis import (
    given,
    settings,
    strategies as st,
)

from tests.fixtures import (
    account,
    tick_math
)

MIN_TICK = -887272
MAX_TICK = 887272


def test_throws_for_too_low(tick_math):
    with ape.reverts("T"):
        tick_math.get_sqrt_ratio_at_tick(MIN_TICK-1)

def test_throws_for_too_high(tick_math):
    with ape.reverts("T"):
        tick_math.get_sqrt_ratio_at_tick(MAX_TICK+1)


def test_min_tick(tick_math):
    assert tick_math.get_sqrt_ratio_at_tick(MIN_TICK) == 4295128739

def test_min_tick_plus_one(tick_math):
    assert tick_math.get_sqrt_ratio_at_tick(MIN_TICK+1) == 4295343490

def test_max_tick_minus_one(tick_math):
    assert tick_math.get_sqrt_ratio_at_tick(MAX_TICK-1) == 1461373636630004318706518188784493106690254656249

def test_min_tick_ratio_is_less_than_js_implementation(tick_math):
    assert tick_math.get_sqrt_ratio_at_tick(MIN_TICK) < 340282366920938463463374607431768211456

def test_max_tick_minus_one(tick_math):
    assert tick_math.get_sqrt_ratio_at_tick(MAX_TICK-1) == 1461373636630004318706518188784493106690254656249

def test_max_tick_ratio_is_greater_than_js_implementation(tick_math):
    assert tick_math.get_sqrt_ratio_at_tick(MAX_TICK) > 340282366920938463463374607431768211456

def test_max_tick(tick_math):
    assert tick_math.get_sqrt_ratio_at_tick(MAX_TICK) == 1461446703485210103287273052203988822378723970342

def test_price_in_range(tick_math):
    import math
    for abs_tick in [50, 100, 250, 500, 1_000, 2_500, 3_000, 4_000, 5_000, 50_000, 150_000, 250_000, 500_000, 738_203]:
        pyResult = math.sqrt(1.0001 ** abs_tick) * (2 ** 96)
        result = tick_math.get_sqrt_ratio_at_tick(abs_tick)
        abs_diff = abs(result - pyResult)
        assert abs_diff / pyResult < 0.000001