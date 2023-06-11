import ape
import pytest
from hypothesis import (
    given,
    settings,
    strategies as st,
)

from tests.fixtures import *

@pytest.mark.profile
def test_add_asset_profile(cog_pair, accounts, chain, collateral, asset, oracle):
    account = accounts[0]

    oracle.setPrice(5000000000000000000, sender=account)
    oracle.setUpdated(True, sender=account)
    cog_pair.get_exchange_rate(sender=account)

    asset.mint(account, 10**18, sender=account)
    asset.approve(cog_pair, 10**18, sender=account)
    reciept = cog_pair.deposit(10**18, account, sender=account)

    print("Deposit Gas Used {used}".format(used=reciept.gas_used))

    account = accounts[1]

    asset.mint(account, 10**18, sender=account)
    asset.approve(cog_pair, 10**18, sender=account)
    reciept = cog_pair.deposit(10**18, account, sender=account)
    
    print("Mint Gas Used {used}".format(used=reciept.gas_used))

    account = accounts[0]

    reciept = cog_pair.withdraw(10**18, account, sender=account)

    print("Withdraw Gas Used {used}".format(used=reciept.gas_used))

    account = accounts[1]

    reciept = cog_pair.redeem(9**18, account, sender=account)

    print("Redeem Gas Used {used}".format(used=reciept.gas_used))

    account = accounts[2]

    collateral.mint(account, 10**18, sender=account)
    collateral.approve(cog_pair, 10**18, sender=account)
    cog_pair.add_collateral(account, 10**18, sender=account)

    print("Add Collateral Gas Used {used}".format(used=reciept.gas_used))

    reciept = cog_pair.remove_collateral(account, 10**18, sender=account)

    print("Remove Collateral Gas Used {used}".format(used=reciept.gas_used))

    account = accounts[0]

    collateral.mint(account, 10**18, sender=account)
    collateral.approve(cog_pair, 10**18, sender=account)
    cog_pair.add_collateral(account, 10**18, sender=account)

    reciept = cog_pair.borrow(account, 3**18, sender=account)
    print("Borrow Gas Used {used}".format(used=reciept.gas_used))

    asset.mint(account, 3**18, sender=account)
    asset.approve(cog_pair, 3**18, sender=account)

    reciept = cog_pair.repay(account, 3**18, sender=account)

    print("Repay Gas Used {used}".format(used=reciept.gas_used))

    assert False