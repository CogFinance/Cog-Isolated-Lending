# @version 0.3.7
# @author tinkermaster-overspark

from vyper.interfaces import ERC20

# ///////////////////////////////////////////////////// #
#						Rebase Stuff					#
# ///////////////////////////////////////////////////// #

struct Rebase:
    elastic: uint128
    base: uint128

@pure
@internal
def to_base(total: Rebase, elastic: uint256, round_up: bool) -> uint256:
    """
    @param total - The Rebase which should be used to convert the elastic value to a relative base value
    @param elastic - The elastic value to convert to a base value
    @param round_up - Whether or not to round up the resulting base value
    """
    if total.elastic == 0:
        return elastic
    else:
        base: uint256 = (elastic * convert(total.base, uint256)) / convert(
            total.elastic, uint256
        )
        if round_up and (
            (
                (base * convert(total.elastic, uint256))
                / convert(total.base, uint256)
            )
            < elastic
        ):
            base = base + 1
        return base

@pure
@internal
def to_elastic(total: Rebase, base: uint256, round_up: bool) -> uint256:
    """
    @param total - The Rebase which should be used to convert the base value to a relative elastic value
    @param base - The base value to convert to an elastic value
    @param round_up - Whether or not to round up the resulting elastic value
    """
    if total.base == 0:
        return base
    else:
        elastic: uint256 = (base * convert(total.elastic, uint256)) / convert(
            total.base, uint256
        )
        if round_up and (
            (
                (elastic * convert(total.base, uint256))
                / convert(total.elastic, uint256)
            )
            < base
        ):
            elastic = elastic + 1
        return elastic

@internal
def add(total: Rebase, elastic: uint256, round_up: bool) -> (Rebase, uint256):
    """
    @param total - The rebase to add the elastic value to
    @param elastic - The elastic value to add to the rebase
    @param round_up - Whether or not to round up the resulting Rebase

    @return - The new Rebase and the base value of the elastic value
    """
    base: uint256 = self.to_base(total, elastic, round_up)
    total.elastic += convert(elastic, uint128)
    total.base += convert(base, uint128)
    return (total, base)

@internal
def sub(total: Rebase, base: uint256, round_up: bool) -> (Rebase, uint256):
    """
    @param total - The rebase to subtract the base value from
    @param base - The base value to subtract from the rebase
    @param round_up - Whether or not to round up the resulting Rebase

    @return - The new Rebase and the elastic value of the base value
    """
    elastic: uint256 = self.to_elastic(total, base, round_up)
    total.elastic -= convert(elastic, uint128)
    total.base -= convert(base, uint128)
    return (total, elastic)

# ///////////////////////////////////////////////////// #
#						Interfaces						#
# ///////////////////////////////////////////////////// #

# Oracle Interface
interface IOracle:
    def get() -> (bool, uint256): nonpayable

# ERC20 Events

event Transfer:
    sender: indexed(address)
    receiver: indexed(address)
    amount: uint256

event Approval:
    owner: indexed(address)
    spender: indexed(address)
    allowance: uint256

# ERC4646 Events

event Deposit:
    depositor: indexed(address)
    receiver: indexed(address)
    assets: uint256
    shares: uint256

event Withdraw:
    withdrawer: indexed(address)
    receiver: indexed(address)
    owner: indexed(address)
    assets: uint256
    shares: uint256

# ///////////////////////////////////////////////////// #
#					State Variables						#
# ///////////////////////////////////////////////////// #

oracle: public(address) # Address of the oracle
asset: public(address) # Address of the asset
collateral: public(address) # Address of the collateral

total_collateral_share: public(uint256) # Total collateral share of all borrowers
total_asset: public(Rebase) # Numerator is amount asset total, denominator keeps track of total shares of the asset
total_borrow: public(Rebase) # Numerator is the amount owed total, denominator keeps track of initial borrow shares owed

user_collateral_share: public(HashMap[address, uint256]) # Collateral share of each user
user_borrow_part: public(HashMap[address, uint256]) # Borrow part of each user

exchange_rate: public(uint256) # Exchange rate between asset and collateral

struct AccrueInfo:
        interest_per_second: uint64
        last_accrued: uint64
        fees_earned_fraction: uint128

accrue_info: public(AccrueInfo) # General Info for keeping track of interest rate and fees earned

# ///////////////////////////////////////////////////// #
#		        Configuration Constants	            	#
# ///////////////////////////////////////////////////// #
EXCHANGE_RATE_PRECISION: constant(uint256) = 1000000000000000000  # 1e18

COLLATERIZATION_RATE_PRECISION: constant(uint256) = 100000  # 1e5
OPEN_COLLATERIZATION_RATE: constant(uint256) = 77000  # 77%
CLOSED_COLLATERIZATION_RATE: constant(uint256) = 75000  # 75%

BORROW_OPENING_FEE: constant(uint256) = 50
BORROW_OPENING_FEE_PRECISION: constant(uint256) = 100000

STARTING_INTEREST_PER_SECOND: constant(uint64) = 317097920  # 1% APR

PROTOCOL_FEE: constant(uint256) = 100000  # 10%
PROTOCOL_FEE_DIVISOR: constant(uint256) = 100000

UTILIZATION_PRECISION: constant(uint256) = 1000000000000000000  # 1e18
MINIMUM_TARGET_UTILIZATION: constant(uint256) = 600000000000000000  # 60%
MAXIMUM_TARGET_UTILIZATION: constant(uint256) = 800000000000000000  # 80%
FACTOR_PRECISION: constant(uint256) = 1000000000000000000  # 1e18

MAXIMUM_INTEREST_PER_SECOND: constant(uint64) = 79274480  # Aprox 1000% APR
MINIMUM_INTEREST_PER_SECOND: constant(uint64) = 79274480  # Aprox 0.25% APR
INTEREST_ELASTICITY: constant(
    uint256
) = 28800000000000000000000000000000000000000  # 2.88e40

# //////////////////////////////////////////////////////////////// #
#                              ERC20                               # 
# //////////////////////////////////////////////////////////////// #
balanceOf: public(HashMap[address, uint256])

@external
def totalSupply() -> uint256:
    """
    @return - Returns the total supply of the Asset Token, which is the number of claims (shares) 
    on all Assets in the pool
    """
    return convert(self.total_asset.base, uint256)

allowance: public(HashMap[address, HashMap[address, uint256]])

NAME: constant(String[14]) = "Cog Pool Token"

@external
def name() -> String[14]:
    return NAME

SYMBOL: constant(String[3]) = "COG"

@external
def symbol() -> String[3]:
    return SYMBOL

DECIMALS: constant(uint8) = 18

@external
def decimals() -> uint8:
    return DECIMALS

@external
def transfer(receiver: address, amount: uint256) -> bool:
    self.balanceOf[msg.sender] -= amount
    self.balanceOf[receiver] += amount
    # log Transfer(msg.sender, receiver, amount)
    return True


@external
def approve(spender: address, amount: uint256) -> bool:
    self.allowance[msg.sender][spender] = amount
    # log Approval(msg.sender, spender, amount)
    return True


@external
def transferFrom(sender: address, receiver: address, amount: uint256) -> bool:
    self.allowance[sender][msg.sender] -= amount
    self.balanceOf[sender] -= amount
    self.balanceOf[receiver] += amount
    # log Transfer(sender, receiver, amount)
    return True

# ///////////////////////////////////////////////////// #
#		            ERC4626 Compatibility	        	#
# ///////////////////////////////////////////////////// #

@view
@external
def totalAssets() -> uint256:
    return convert(self.total_asset.base, uint256)

@view
@external
def convertToAssets(shareAmount: uint256) -> uint256:
    return self.to_base(self.total_asset, shareAmount, False)

@view
@external
def convertToShares(assetAmount: uint256) -> uint256:
    return self.to_elastic(self.total_asset, assetAmount, False)

@view
@external
def maxDeposit(owner: address) -> uint256:
    return MAX_UINT256

@view
@external
def previewDeposit(assets: uint256) -> uint256:
    return 0

@external
def deposit(assets: uint256, receiver: address=msg.sender) -> uint256:
    return 0

@view
@external
def maxMint(owner: address) -> uint256:
    return 0

@view
@external
def previewMint(shares: uint256) -> uint256:
    return 0

@external
def mint(shares: uint256, receiver: address=msg.sender) -> uint256:
    return 0

@view
@external
def maxWithdraw(owner: address) -> uint256:
    return 0

@view
@external
def previewWithdraw(assets: uint256) -> uint256:
    return 0

@external
def withdraw(assets: uint256, receiver: address=msg.sender, owner: address=msg.sender) -> uint256:
    return 0

@view
@external
def maxRedeem(owner: address) -> uint256:
    return 0

@view
@external
def previewRedeem(shares: uint256) -> uint256:
    return 0

@external
def redeem(shares: uint256, receiver: address=msg.sender, owner: address=msg.sender) -> uint256:
    return 0


# ///////////////////////////////////////////////////// #
# 		        Internal Implementations	         	#
# ///////////////////////////////////////////////////// #
@internal
def _accrue():
    _accrue_info: AccrueInfo = self.accrue_info
    elapsed_time: uint256 = block.timestamp - convert(
        _accrue_info.last_accrued, uint256
    )
    if elapsed_time == 0:
        return
    _accrue_info.last_accrued = convert(block.timestamp, uint64)

    _total_borrow: Rebase = self.total_borrow
    if _total_borrow.base == 0:
        if _accrue_info.interest_per_second != STARTING_INTEREST_PER_SECOND:
            _accrue_info.interest_per_second = STARTING_INTEREST_PER_SECOND
        self.accrue_info = _accrue_info
        return

    extra_amount: uint256 = 0
    fee_fraction: uint256 = 0
    _total_asset: Rebase = self.total_asset

    # Accrue interest
    extra_amount = (
        convert(_total_borrow.elastic, uint256)
        * convert(_accrue_info.interest_per_second, uint256)
        * elapsed_time
        / 1000000000000000000
    )  # 1e18
    _total_borrow.elastic = _total_borrow.elastic + convert(
        extra_amount, uint128
    )
    full_asset_amount: uint256 = convert(
        _total_asset.elastic, uint256
    ) + convert(_total_borrow.elastic, uint256)

    # Calculate fees
    fee_amount: uint256 = (
        extra_amount * PROTOCOL_FEE / PROTOCOL_FEE_DIVISOR
    )  # % of interest paid goes to fee
    fee_fraction = (
        fee_amount * convert(_total_asset.base, uint256) / full_asset_amount
    )
    _accrue_info.fees_earned_fraction = (
        _accrue_info.fees_earned_fraction + convert(fee_fraction, uint128)
    )
    _total_asset.base = _total_asset.base + convert(fee_fraction, uint128)
    self.total_borrow = _total_borrow

    # Update interest rate
    utilization: uint256 = (
        convert(_total_borrow.elastic, uint256)
        * UTILIZATION_PRECISION
        / full_asset_amount
    )
    if utilization < MINIMUM_TARGET_UTILIZATION:
        under_factor: uint256 = (
            (MINIMUM_TARGET_UTILIZATION - utilization)
            * FACTOR_PRECISION
            / MINIMUM_TARGET_UTILIZATION
        )
        scale: uint256 = INTEREST_ELASTICITY + (
            under_factor * under_factor * elapsed_time
        )
        _accrue_info.interest_per_second = convert(
            convert(_accrue_info.interest_per_second, uint256)
            * INTEREST_ELASTICITY
            / scale,
            uint64,
        )

        if _accrue_info.interest_per_second < MINIMUM_INTEREST_PER_SECOND:
            _accrue_info.interest_per_second = (
                MINIMUM_INTEREST_PER_SECOND  # 0.25% APR minimum
            )
    elif utilization > MAXIMUM_TARGET_UTILIZATION:
        over_factor: uint256 = (
            (utilization - MAXIMUM_TARGET_UTILIZATION)
            * FACTOR_PRECISION
            / MAXIMUM_TARGET_UTILIZATION
        )
        scale: uint256 = INTEREST_ELASTICITY + (
            over_factor * over_factor * elapsed_time
        )
        _accrue_info.interest_per_second = convert(
            convert(_accrue_info.interest_per_second, uint256)
            * scale
            / INTEREST_ELASTICITY,
            uint64,
        )
        new_interest_per_second: uint64 = _accrue_info.interest_per_second

        if new_interest_per_second > MAXIMUM_INTEREST_PER_SECOND:
            _accrue_info.interest_per_second = (
                MAXIMUM_INTEREST_PER_SECOND  # 100% APR maximum
            )
        _accrue_info.interest_per_second = new_interest_per_second

    self.accrue_info = _accrue_info


@internal
def _add_collateral(to: address, amount: uint256):
    self.user_collateral_share[to] = self.user_collateral_share[to] + amount
    old_total_collateral_share: uint256 = self.total_collateral_share
    self.total_collateral_share = old_total_collateral_share + amount
    assert ERC20(self.collateral).transferFrom(
        msg.sender, self, amount
    ), "TransferFrom Failed"


@internal
def _remove_collateral(to: address, amount: uint256):
    self.user_collateral_share[msg.sender] = (
        self.user_collateral_share[msg.sender] - amount
    )
    self.total_collateral_share = self.total_collateral_share - amount
    assert ERC20(self.collateral).transfer(to, amount), "Transfer Failed"


@internal
def _add_asset(to: address, amount: uint256) -> uint256:
    _total_asset: Rebase = self.total_asset
    total_asset_share: uint256 = convert(_total_asset.elastic, uint256)
    all_share: uint256 = convert(
        _total_asset.elastic + self.total_borrow.elastic, uint256
    )
    fraction: uint256 = 0
    if all_share == 0:
        fraction = amount
    else:
        fraction = (amount * convert(_total_asset.base, uint256)) / all_share
    if _total_asset.base + convert(fraction, uint128) < 1000:
        return 0

    self.total_asset = Rebase(
        {
            elastic: self.total_asset.elastic + convert(amount, uint128),
            base: self.total_asset.base + convert(fraction, uint128),
        }
    )

    self.balanceOf[to] = self.balanceOf[to] + fraction

    assert ERC20(self.asset).transferFrom(
        msg.sender, self, amount
    ), "TransferFrom Failed"
    return fraction


@internal
def _remove_asset(to: address, amount: uint256) -> uint256:
    _total_asset: Rebase = self.total_asset
    all_share: uint256 = convert(
        _total_asset.elastic + self.total_borrow.elastic, uint256
    )
    share: uint256 = (amount * all_share) / convert(_total_asset.base, uint256)
    self.balanceOf[msg.sender] = self.balanceOf[msg.sender] - amount

    _total_asset.elastic -= convert(amount, uint128)
    _total_asset.base -= convert(amount, uint128)
    assert _total_asset.base >= 1000, "Below Minimum"
    self.total_asset = _total_asset

    assert ERC20(self.asset).transfer(to, amount), "Transfer Failed"

    return share


@internal
def _update_exchange_rate() -> (bool, uint256):
    updated: bool = False
    rate: uint256 = 0
    oracle_addr: address = self.oracle

    updated, rate = IOracle(oracle_addr).get()

    if updated:
        self.exchange_rate = rate
    else:
        rate = self.exchange_rate

    return (updated, rate)


@internal
def _borrow(to: address, amount: uint256) -> uint256:
    self._update_exchange_rate()
    fee_amount: uint256 = (
        amount * BORROW_OPENING_FEE
    ) / BORROW_OPENING_FEE_PRECISION

    temp_total_borrow: Rebase = Rebase(
        {
            elastic: 0,
            base: 0,
        }
    )
    part: uint256 = 0

    temp_total_borrow, part = self.add(
        self.total_borrow, (amount + fee_amount), True
    )
    self.total_borrow = temp_total_borrow
    self.user_borrow_part[msg.sender] = self.user_borrow_part[msg.sender] + part

    _total_asset: Rebase = self.total_asset
    assert _total_asset.base >= 1000, "Below Minimum"
    _total_asset.elastic = _total_asset.elastic - convert(amount, uint128)
    self.total_asset = _total_asset
    assert ERC20(self.asset).transfer(to, amount), "Transfer Failed"
    return amount


@internal
def _repay(to: address, payment: uint256) -> uint256:
    temp_total_borrow: Rebase = Rebase(
        {
            elastic: 0,
            base: 0,
        }
    )
    amount: uint256 = 0

    temp_total_borrow, amount = self.sub(self.total_borrow, payment, True)
    self.total_borrow = temp_total_borrow

    self.user_borrow_part[to] = self.user_borrow_part[to] - payment
    total_share: uint128 = self.total_asset.elastic
    assert ERC20(self.asset).transferFrom(
        msg.sender, self, payment
    ), "TransferFrom Failed"
    self.total_asset.elastic = total_share + convert(amount, uint128)
    return amount


@internal
def _is_solvent(user: address, open: bool, exchange_rate: uint256) -> bool:
    borrow_part: uint256 = self.user_borrow_part[user]
    if borrow_part == 0:
        return True
    collateral_share: uint256 = self.user_collateral_share[user]
    if collateral_share == 0:
        return False

    _total_borrow: Rebase = self.total_borrow
    collateral: uint256 = 0
    if open:
        collateral = (
            collateral_share
            * EXCHANGE_RATE_PRECISION
            / COLLATERIZATION_RATE_PRECISION
            * OPEN_COLLATERIZATION_RATE
        )
    else:
        collateral = (
            collateral_share
            * EXCHANGE_RATE_PRECISION
            / COLLATERIZATION_RATE_PRECISION
            * CLOSED_COLLATERIZATION_RATE
        )

    borrow_part = (
        borrow_part * convert(_total_borrow.elastic, uint256) * exchange_rate
    ) / convert(_total_borrow.base, uint256)

    return collateral >= borrow_part


# ///////////////////////////////////////////////////// #
# 				External Implementations				#
# ///////////////////////////////////////////////////// #
@external
def setup(_asset: address, _collateral: address, _oracle: address):
    assert (
        self.collateral == 0x0000000000000000000000000000000000000000
        and _collateral != 0x0000000000000000000000000000000000000000
    ), "Pair already initialized"
    self.asset = _asset
    self.collateral = _collateral
    self.oracle = _oracle


@external
def accrue():
    self._accrue()

@external
def add_collateral(to: address, amount: uint256):
    self._accrue()
    self._add_collateral(to, amount)


@external
def remove_collateral(to: address, amount: uint256):
    self._accrue()
    self._remove_collateral(to, amount)
    assert self._is_solvent(
        msg.sender, False, self.exchange_rate
    ), "Insufficient Collateral"


@external
def add_asset(to: address, amount: uint256) -> uint256:
    self._accrue()
    return self._add_asset(to, amount)


@external
def remove_asset(to: address, amount: uint256) -> uint256:
    self._accrue()
    return self._remove_asset(to, amount)


@external
def borrow(to: address, amount: uint256) -> uint256:
    self._accrue()
    borrowed: uint256 = self._borrow(to, amount)
    assert self._is_solvent(
        msg.sender, False, self.exchange_rate
    ), "Insufficient Collateral"
    return borrowed


@external
def repay(to: address, payment: uint256) -> uint256:
    self._accrue()
    return self._repay(to, payment)


@external
def get_exchange_rate() -> (bool, uint256):
    return self._update_exchange_rate()