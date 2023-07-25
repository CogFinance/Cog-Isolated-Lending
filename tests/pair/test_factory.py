import boa
import pytest
from hypothesis import (
    given,
    settings,
    strategies as st,
)

from tests.fixtures import *

def test_admin_controls(cog_factory, accounts, account):
    assert cog_factory.owner() == account

    with boa.reverts("Ownable2Step: caller is not the owner"):
        cog_factory.transfer_ownership(accounts[5], sender=accounts[3])

    cog_factory.transfer_ownership(accounts[2], sender=account)

    with boa.reverts("Ownable2Step: caller is not the new owner"):
        cog_factory.accept_ownership(sender=accounts[7])

    assert cog_factory.pending_owner() == accounts[2]

    cog_factory.accept_ownership(sender=accounts[2])

    cog_factory.change_fee_to(accounts[4], sender=accounts[2])
    assert cog_factory.fee_to() == accounts[4]


    with boa.reverts("Ownable2Step: caller is not the owner"):
        cog_factory.renounce_ownership(sender=account)

    cog_factory.renounce_ownership(sender=accounts[2])

    assert cog_factory.owner() == "0x0000000000000000000000000000000000000000"

    with boa.reverts():
        cog_factory.change_fee_to(accounts[4], sender=accounts[2])

def test_deploy_pairs(cog_factory, cog_pair_blueprint, account, asset, collateral, oracle):
    cog_factory.deploy_stable_risk_pair(asset,collateral,oracle, sender=account)

    cog_factory.deploy_low_risk_pair(asset,collateral,oracle, sender=account)
    cog_factory.deploy_medium_risk_pair(asset,collateral,oracle, sender=account)
    cog_factory.deploy_high_risk_pair(asset,collateral,oracle, sender=account)

    cog_factory.deploy_custom_risk_pair(
        asset, collateral, oracle, cog_pair_blueprint, 3, 600000000000000000, 800000000000000000, 1585489600, 634195840, 317097920000, sender=account
    )
