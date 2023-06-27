import boa
import pytest
from hypothesis import (
    given,
    settings,
    strategies as st,
)

from tests.fixtures import *

def test_pause_and_unpause(cog_pair, asset, cog_factory, account):
    cog_factory.set_priv_user_status(account, True, sender=account)
    
    cog_factory.pause(cog_pair, sender=account)
    assert cog_pair.paused() == True

    asset.mint(account, 1000000000000000000, sender=account)
    asset.approve(cog_pair, 1000000000000000000, sender=account)
    with boa.reverts():
        cog_pair.deposit(1000000000000000000, account, sender=account)

    cog_factory.unpause(cog_pair, sender=account)

    cog_pair.deposit(1000000000000000000, account, sender=account)

    cog_factory.set_priv_user_status(account, False, sender=account)

    with boa.reverts():
        cog_factory.pause(cog_pair, sender=account)

def test_fee_setting(cog_pair, asset, cog_factory, account):
    with boa.reverts():
        cog_factory.update_default_protocol_fee(cog_pair, 1000001, sender=account)
    
    cog_factory.update_default_protocol_fee(cog_pair, 500000, sender=account)

    assert cog_pair.DEFAULT_PROTOCOL_FEE() == 500000

    # update_borrow_fee

    cog_factory.update_borrow_fee(cog_pair, 100, sender=account)

    assert cog_pair.BORROW_OPENING_FEE() == 100

    with boa.reverts():
        cog_factory.update_borrow_fee(cog_pair, 50001, sender=account)
