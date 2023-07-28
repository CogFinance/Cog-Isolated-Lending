import pytest
import boa

from datetime import timedelta

from hypothesis import (
    given,
    settings,
    strategies as st,
)

from tests.fixtures import *

@given(
    amount_one=st.integers(min_value=100000, max_value=2**128-1),
    amount_two=st.integers(min_value=100000, max_value=2**128-1),
    amount_three=st.integers(min_value=100000, max_value=2**128-1),
    amount_four=st.integers(min_value=100000, max_value=2**128-1),
)
@settings(max_examples=10, deadline=None)
def test_fusebox(account, accounts, fuse_one, fuse_two, fuse_three, fuse_four, fuse_box, amount_one, amount_two, amount_three, amount_four):
    fuse_one.setPrice(amount_one)
    fuse_two.setPrice(amount_two)
    fuse_three.setPrice(amount_three)
    fuse_four.setPrice(amount_four)

    fuse_one.setUpdated(True)
    fuse_two.setUpdated(True)
    fuse_three.setUpdated(True)
    fuse_four.setUpdated(True)

    # How can you value cpu cycles when good security is priceless
    for i_0 in range(2):
        for i_1 in range(2):
            for i_2 in range(2):
                for i_3 in range(2):
                    active_sources = i_0 + i_1 + i_2 + i_3
                    if active_sources == 0:
                        continue

                    expected_avg = amount_one + amount_two + amount_three + amount_four

                    with boa.env.prank(account):
                        if i_0 == 0:
                            expected_avg -= amount_one
                            fuse_box.defuse_source(0)
                        else:
                            fuse_box.activate_source(0)

                        if i_1 == 0:
                            expected_avg -= amount_two
                            fuse_box.defuse_source(1)
                        else:
                            fuse_box.activate_source(1)

                        if i_2 == 0:
                            expected_avg -= amount_three
                            fuse_box.defuse_source(2)
                        else:
                            fuse_box.activate_source(2)

                        if i_3 == 0:
                            expected_avg -= amount_four
                            fuse_box.defuse_source(3)
                        else:
                            fuse_box.activate_source(3)

                        (updated, price) = fuse_box.get()

                        assert price == pytest.approx(expected_avg / active_sources, 1)

def test_admin_controls(fuse_box, accounts, account):
    assert fuse_box.owner() == account

    with boa.reverts("Ownable2Step: caller is not the owner"):
        fuse_box.transfer_ownership(accounts[5], sender=accounts[3])

    fuse_box.transfer_ownership(accounts[2], sender=account)

    with boa.reverts("Ownable2Step: caller is not the new owner"):
        fuse_box.accept_ownership(sender=accounts[7])

    assert fuse_box.pending_owner() == accounts[2]

    fuse_box.accept_ownership(sender=accounts[2])

    with boa.reverts("Ownable2Step: caller is not the owner"):
        fuse_box.renounce_ownership(sender=account)

    fuse_box.renounce_ownership(sender=accounts[2])

    assert fuse_box.owner() == "0x0000000000000000000000000000000000000000"

