# @version 0.3.7

"""
@title CogPair
@author cog.finance
@license GNU Affero General Public License v3.0
@notice Implementation of an isolated lending pool with PoL in Vyper
@dev ERC20 support for True/revert, return True/False, return None, ty Curve for the inspiration
"""

from vyper.interfaces import ERC20
from vyper.interfaces import ERC20Detailed
from vyper.interfaces import ERC4626

implements: ERC20
implements: ERC4626

# ///////////////////////////////////////////////////// #
#                  Rebase Math Helpers                  #
# ///////////////////////////////////////////////////// #

struct Rebase:
        elastic: uint128
        base: uint128


@pure
@internal
def to_base(total: Rebase, elastic: uint256, round_up: bool) -> uint256:
    """
    @param total - The Rebase value which should be used to dervie the relative base value
    @param elastic - The elastic value to convert to a relative base value
    @param round_up - Self explanatory
    """
    if total.elastic == 0:
        # If elastic is 0, then 0/n = 0 ∀ n ∈ R
        return elastic
    else:
        # Base is equal to elastic * (total.base / total.elastic), essentially a ratio
        base: uint256 = (elastic * convert(total.base, uint256)) / convert(
            total.elastic, uint256
        )

        # mamushi: Exhibit 1
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
    @param total - The Rebase which should be used to derive the relative elastic value
    @param base - The base value to convert to a relative elastic value
    @param round_up - Self explanatory
    """
    if total.base == 0:
        # If base is 0, then Rebase would be n/n, so elastic = base
        return base
    else:
        # Elastic is equal to base * (total.elastic / total.base), essentially a ratio
        elastic: uint256 = (base * convert(total.elastic, uint256)) / convert(
            total.base, uint256
        )

        # mamushi: Exhibit 2
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
    @notice Add `elastic` to `total` and doubles `total.base`

    @param total - The current total
    @param elastic - The elastic value to add to the rebase
    @param round_up - Self explanatory

    @return - The new Rebase total
    @return - The base in relationship to the elastic value
    """
    base: uint256 = self.to_base(total, elastic, round_up)
    total.elastic += convert(elastic, uint128)
    total.base += convert(base, uint128)
    return (total, base)


@internal
def sub(total: Rebase, base: uint256, round_up: bool) -> (Rebase, uint256):
    """
    @param total - The current total
    @param base - The base value to subtract from the rebase total
    @param round_up - Self explanatory

    @return - The new Rebase total
    @return - The elastic in relationship to the base value
    """
    elastic: uint256 = self.to_elastic(total, base, round_up)
    total.elastic -= convert(elastic, uint128)
    total.base -= convert(base, uint128)
    return (total, elastic)


# ///////////////////////////////////////////////////// #
#		      Math Helper For Precision					#
# ///////////////////////////////////////////////////// #
# Ty snekmate again
@pure
@internal
def mul_div(
    x: uint256, y: uint256, denominator: uint256, roundup: bool
) -> uint256:
    """
    @dev Calculates "(x * y) / denominator" in 512-bit precision,
         following the selected rounding direction.
    @notice The implementation is inspired by Remco Bloemen's
            implementation under the MIT license here:
            https://xn--2-umb.com/21/muldiv.
            Furthermore, the rounding direction design pattern is
            inspired by OpenZeppelin's implementation here:
            https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/utils/math/Math.sol.
    @param x The 32-byte multiplicand.
    @param y The 32-byte multiplier.
    @param denominator The 32-byte divisor.
    @param roundup The Boolean variable that specifies whether
           to round up or not. The default `False` is round down.
    @return uint256 The 32-byte calculation result.
    """
    # Handle division by zero.
    assert denominator != empty(uint256), "Math: mul_div division by zero"

    # 512-bit multiplication "[prod1 prod0] = x * y".
    # Compute the product "mod 2**256" and "mod 2**256 - 1".
    # Then use the Chinese Remainder theorem to reconstruct
    # the 512-bit result. The result is stored in two 256-bit
    # variables, where: "product = prod1 * 2**256 + prod0".
    mm: uint256 = uint256_mulmod(x, y, max_value(uint256))
    # The least significant 256 bits of the product.
    prod0: uint256 = unsafe_mul(x, y)
    # The most significant 256 bits of the product.
    prod1: uint256 = empty(uint256)

    if mm < prod0:
        prod1 = unsafe_sub(unsafe_sub(mm, prod0), 1)
    else:
        prod1 = unsafe_sub(mm, prod0)

    if prod1 == empty(uint256):
        if roundup and uint256_mulmod(x, y, denominator) != empty(uint256):
            # Calculate "ceil((x * y) / denominator)". The following
            # line cannot overflow because we have the previous check
            # "(x * y) % denominator != 0", which accordingly rules out
            # the possibility of "x * y = 2**256 - 1" and `denominator == 1`.
            return unsafe_add(unsafe_div(prod0, denominator), 1)
        else:
            return unsafe_div(prod0, denominator)

    # Ensure that the result is less than 2**256. Also,
    # prevents that `denominator == 0`.
    assert denominator > prod1, "Math: mul_div overflow"

    #######################
    # 512 by 256 Division #
    #######################

    # Make division exact by subtracting the remainder
    # from "[prod1 prod0]". First, compute remainder using
    # the `uint256_mulmod` operation.
    remainder: uint256 = uint256_mulmod(x, y, denominator)

    # Second, subtract the 256-bit number from the 512-bit
    # number.
    if remainder > prod0:
        prod1 = unsafe_sub(prod1, 1)
    prod0 = unsafe_sub(prod0, remainder)

    # Factor powers of two out of the denominator and calculate
    # the largest power of two divisor of denominator. Always `>= 1`,
    # unless the denominator is zero (which is prevented above),
    # in which case `twos` is zero. For more details, please refer to:
    # https://cs.stackexchange.com/q/138556.

    # The following line does not overflow because the denominator
    # cannot be zero at this stage of the function.
    twos: uint256 = denominator & (unsafe_add(~denominator, 1))
    # Divide denominator by `twos`.
    denominator_div: uint256 = unsafe_div(denominator, twos)
    # Divide "[prod1 prod0]" by `twos`.
    prod0 = unsafe_div(prod0, twos)
    # Flip `twos` such that it is "2**256 / twos". If `twos` is zero,
    # it becomes one.
    twos = unsafe_add(unsafe_div(unsafe_sub(empty(uint256), twos), twos), 1)

    # Shift bits from `prod1` to `prod0`.
    prod0 |= unsafe_mul(prod1, twos)

    # Invert the denominator "mod 2**256". Since the denominator is
    # now an odd number, it has an inverse modulo 2**256, so we have:
    # "denominator * inverse = 1 mod 2**256". Calculate the inverse by
    # starting with a seed that is correct for four bits. That is,
    # "denominator * inverse = 1 mod 2**4".
    inverse: uint256 = unsafe_mul(3, denominator_div) ^ 2

    # Use Newton-Raphson iteration to improve accuracy. Thanks to Hensel's
    # lifting lemma, this also works in modular arithmetic by doubling the
    # correct bits in each step.
    inverse = unsafe_mul(
        inverse, unsafe_sub(2, unsafe_mul(denominator_div, inverse))
    )  # Inverse "mod 2**8".
    inverse = unsafe_mul(
        inverse, unsafe_sub(2, unsafe_mul(denominator_div, inverse))
    )  # Inverse "mod 2**16".
    inverse = unsafe_mul(
        inverse, unsafe_sub(2, unsafe_mul(denominator_div, inverse))
    )  # Inverse "mod 2**32".
    inverse = unsafe_mul(
        inverse, unsafe_sub(2, unsafe_mul(denominator_div, inverse))
    )  # Inverse "mod 2**64".
    inverse = unsafe_mul(
        inverse, unsafe_sub(2, unsafe_mul(denominator_div, inverse))
    )  # Inverse "mod 2**128".
    inverse = unsafe_mul(
        inverse, unsafe_sub(2, unsafe_mul(denominator_div, inverse))
    )  # Inverse "mod 2**256".

    # Since the division is now exact, we can divide by multiplying
    # with the modular inverse of the denominator. This returns the
    # correct result modulo 2**256. Since the preconditions guarantee
    # that the result is less than 2**256, this is the final result.
    # We do not need to calculate the high bits of the result and
    # `prod1` is no longer necessary.
    result: uint256 = unsafe_mul(prod0, inverse)

    if roundup and uint256_mulmod(x, y, denominator) != empty(uint256):
        # Calculate "ceil((x * y) / denominator)". The following
        # line uses intentionally checked arithmetic to prevent
        # a theoretically possible overflow.
        result += 1

    return result


# ///////////////////////////////////////////////////// #
#						Interfaces						#
# ///////////////////////////////////////////////////// #

# Oracle Interface
interface IOracle:
    def get() -> (bool, uint256): nonpayable


# Factory Interface
interface ICogFactory:
    def fee_to() -> address: view


# Cog Pair Specific Events
event AddCollateral:
    to: indexed(address)
    amount: indexed(uint256)
    user_collateral_share: indexed(uint256)


event RemoveCollateral:
    to: indexed(address)
    amount: indexed(uint256)
    user_collateral_share: indexed(uint256)


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
#                 State Variables	                    #
# ///////////////////////////////////////////////////// #

oracle: public(immutable(address))  # Address of the oracle
asset: public(immutable(address))  # Address of the asset
collateral: public(immutable(address))  # Address of the collateral

total_collateral_share: public(
    uint256
)  # Total collateral share of all borrowers
total_asset: public(
    Rebase
)  # Numerator is amount asset total, denominator keeps track of total shares of the asset
total_borrow: public(
    Rebase
)  # Numerator is the amount owed total, denominator keeps track of initial borrow shares owed

user_collateral_share: public(
    HashMap[address, uint256]
)  # Collateral share of each user

user_borrow_part: public(
    HashMap[address, uint256]
)  # Borrow ""share"" of each user

exchange_rate: public(uint256)  # Exchange rate between asset and collateral


struct AccrueInfo:
        interest_per_second: uint64
        last_accrued: uint64
        fees_earned_fraction: uint128


struct SurgeInfo:
        last_interest_per_second: uint64
        last_elapsed_time: uint64


accrue_info: public(AccrueInfo)

surge_info: public(SurgeInfo)

factory: public(immutable(address))  # Address of the factory
paused: public(bool)  # Status of if the pool is paused

# ///////////////////////////////////////////////////// #
#          Configuration Constants - ()           #
# ///////////////////////////////////////////////////// #
EXCHANGE_RATE_PRECISION: constant(uint256) = 1000000000000000000  # 1e18

COLLATERIZATION_RATE_PRECISION: constant(uint256) = 100000  # 1e5
COLLATERIZATION_RATE: constant(uint256) = 75000  # 75%

BORROW_OPENING_FEE: public(uint256)
BORROW_OPENING_FEE_PRECISION: constant(uint256) = 100000

protocol_fee: public(
    uint256
)  # Starts at 10%, raised when PoL only mode is activated to PROTOCOL_FEE_DIVISOR or 100%
DEFAULT_PROTOCOL_FEE: public(uint256)
PROTOCOL_FEE_DIVISOR: constant(uint256) = 1000000
# dr/dt, where dt = 1 day (86400), and dr is change in interest_rate per second or 3170979200 (10% interest rate)
PROTOCOL_SURGE_THRESHOLD: constant(
    uint64
) = 36701  # If IR surges ~10% in 1 day then Protocol begins accuring PoL

UTILIZATION_PRECISION: constant(uint256) = 1000000000000000000  # 1e18
MINIMUM_TARGET_UTILIZATION: constant(uint256) = 400000000000000000
MAXIMUM_TARGET_UTILIZATION: constant(uint256) = 800000000000000000  
FACTOR_PRECISION: constant(uint256) = 1000000000000000000  # 1e18

STARTING_INTEREST_PER_SECOND: constant(uint64) = 634195840
MINIMUM_INTEREST_PER_SECOND: constant(uint64) = 79274480
MAXIMUM_INTEREST_PER_SECOND: constant(uint64) = 15854896000 
INTEREST_ELASTICITY: constant(
    uint256
) = 28800000000000000000000000000000000000000  # 2.88e40

LIQUIDATION_MULTIPLIER: constant(uint256) = 112000  # 12
LIQUIDATION_MULTIPLIER_PRECISION: constant(uint256) = 100000  # 1e5

# //////////////////////////////////////////////////////////////// #
#                              ERC20                               #
# //////////////////////////////////////////////////////////////// #
balanceOf: public(HashMap[address, uint256])


@view
@external
def totalSupply() -> uint256:
    """
    @return - Returns the total supply of the Asset Token, which is also the total number of shares
    """
    return convert(self.total_asset.base, uint256)


allowance: public(HashMap[address, HashMap[address, uint256]])

# TODO : Make this composed of the asset and collateral names + Cog Pair
NAME: constant(String[26]) = "Cog Medium Risk Pool Token"


@view
@external
def name() -> String[26]:
    """
    @return The name for the ERC4626 Vault Token
    """
    return NAME


SYMBOL: constant(String[3]) = "COG"


@view
@external
def symbol() -> String[3]:
    """
    @return The token symbol for the ERC4626 Vault Token
    """
    return SYMBOL


DECIMALS: constant(uint8) = 18


@view
@external
def decimals() -> uint8:
    """
    @return The number of decimals for the ERC4626 Vault Token
    """
    return DECIMALS


@external
def transfer(receiver: address, amount: uint256) -> bool:
    self.balanceOf[msg.sender] -= amount
    self.balanceOf[receiver] += amount
    log Transfer(msg.sender, receiver, amount)
    return True


@external
def approve(spender: address, amount: uint256) -> bool:
    self.allowance[msg.sender][spender] = amount
    log Approval(msg.sender, spender, amount)
    return True


@external
def transferFrom(sender: address, receiver: address, amount: uint256) -> bool:
    self.allowance[sender][msg.sender] -= amount
    self.balanceOf[sender] -= amount
    self.balanceOf[receiver] += amount
    log Transfer(sender, receiver, amount)
    return True


# //////////////////////////////////////////////////////////////// #
#                             EIP712                               #
# //////////////////////////////////////////////////////////////// #
# Ty snekmate for this code

# @dev Returns the current on-chain tracked nonce
# of `address`.
nonces: public(HashMap[address, uint256])

# @dev The 32-byte type hash of the `permit` function.
_PERMIT_TYPE_HASH: constant(bytes32) = keccak256(
    "Permit(address owner,address spender,uint256 value,uint256 nonce,uint256 deadline)"
)


# @dev Constant used as part of the ECDSA recovery function.
_MALLEABILITY_THRESHOLD: constant(
    bytes32
) = 0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF5D576E7357A4501DDFE92F46681B20A0


# @dev Caches the domain separator as an `immutable`
# value, but also stores the corresponding chain id
# to invalidate the cached domain separator if the
# chain id changes.
_CACHED_CHAIN_ID: immutable(uint256)
_CACHED_SELF: immutable(address)
_CACHED_DOMAIN_SEPARATOR: immutable(bytes32)


# @dev `immutable` variables to store the name,
# version, and type hash during contract creation.
_HASHED_NAME: immutable(bytes32)
_HASHED_VERSION: immutable(bytes32)
_TYPE_HASH: immutable(bytes32)


@internal
@view
def _domain_separator_v4() -> bytes32:
    """
    @dev Sourced from {EIP712DomainSeparator-domain_separator_v4}.
    @notice See {EIP712DomainSeparator-domain_separator_v4}
            for the function docstring.
    """
    if self == _CACHED_SELF and chain.id == _CACHED_CHAIN_ID:
        return _CACHED_DOMAIN_SEPARATOR
    else:
        return self._build_domain_separator(
            _TYPE_HASH, _HASHED_NAME, _HASHED_VERSION
        )


@internal
@view
def _build_domain_separator(
    type_hash: bytes32, name_hash: bytes32, version_hash: bytes32
) -> bytes32:
    """
    @dev Sourced from {EIP712DomainSeparator-_build_domain_separator}.
    @notice See {EIP712DomainSeparator-_build_domain_separator}
            for the function docstring.
    """
    return keccak256(
        _abi_encode(type_hash, name_hash, version_hash, chain.id, self)
    )


@external
@view
def DOMAIN_SEPARATOR() -> bytes32:
    """
    @dev Returns the domain separator for the current chain.
    @return bytes32 The 32-byte domain separator.
    """
    return self._domain_separator_v4()


@internal
@view
def _hash_typed_data_v4(struct_hash: bytes32) -> bytes32:
    """
    @dev Sourced from {EIP712DomainSeparator-hash_typed_data_v4}.
    @notice See {EIP712DomainSeparator-hash_typed_data_v4}
            for the function docstring.
    """
    return self._to_typed_data_hash(self._domain_separator_v4(), struct_hash)


@internal
@pure
def _to_typed_data_hash(
    domain_separator: bytes32, struct_hash: bytes32
) -> bytes32:
    """
    @dev Sourced from {ECDSA-to_typed_data_hash}.
    @notice See {ECDSA-to_typed_data_hash} for the
            function docstring.
    """
    return keccak256(concat(b"\x19\x01", domain_separator, struct_hash))


@internal
@pure
def _recover_vrs(hash: bytes32, v: uint256, r: uint256, s: uint256) -> address:
    """
    @dev Sourced from {ECDSA-_recover_vrs}.
    @notice See {ECDSA-_recover_vrs} for the
            function docstring.
    """
    return self._try_recover_vrs(hash, v, r, s)


@internal
@pure
def _try_recover_vrs(
    hash: bytes32, v: uint256, r: uint256, s: uint256
) -> address:
    """
    @dev Sourced from {ECDSA-_try_recover_vrs}.
    @notice See {ECDSA-_try_recover_vrs} for the
            function docstring.
    """
    if s > convert(_MALLEABILITY_THRESHOLD, uint256):
        raise "ECDSA: invalid signature 's' value"

    signer: address = ecrecover(hash, v, r, s)
    if signer == empty(address):
        raise "ECDSA: invalid signature"

    return signer


@external
def permit(
    owner: address,
    spender: address,
    amount: uint256,
    deadline: uint256,
    v: uint8,
    r: bytes32,
    s: bytes32,
):
    """
    @dev Sets `amount` as the allowance of `spender`
         over `owner`'s tokens, given `owner`'s signed
         approval.
    @notice Note that `spender` cannot be the zero address.
            Also, `deadline` must be a block timestamp in
            the future. `v`, `r`, and `s` must be a valid
            secp256k1 signature from `owner` over the
            EIP-712-formatted function arguments. Eventually,
            the signature must use `owner`'s current nonce.
    @param owner The 20-byte owner address.
    @param spender The 20-byte spender address.
    @param amount The 32-byte token amount that is
           allowed to be spent by the `spender`.
    @param deadline The 32-byte block timestamp up
           which the `spender` is allowed to spend `amount`.
    @param v The secp256k1 1-byte signature parameter `v`.
    @param r The secp256k1 32-byte signature parameter `r`.
    @param s The secp256k1 32-byte signature parameter `s`.
    """
    assert block.timestamp <= deadline, "ERC20Permit: expired deadline"

    current_nonce: uint256 = self.nonces[owner]
    self.nonces[owner] = unsafe_add(current_nonce, 1)

    struct_hash: bytes32 = keccak256(
        _abi_encode(
            _PERMIT_TYPE_HASH, owner, spender, amount, current_nonce, deadline
        )
    )
    hash: bytes32 = self._hash_typed_data_v4(struct_hash)

    signer: address = self._recover_vrs(
        hash, convert(v, uint256), convert(r, uint256), convert(s, uint256)
    )
    assert signer == owner, "ERC20Permit: invalid signature"

    self.allowance[owner][spender] = amount
    log Approval(owner, spender, amount)


# ///////////////////////////////////////////////////// #
#		            ERC4626 Compatibility	        	#
# ///////////////////////////////////////////////////// #

@view
@external
def totalAssets() -> uint256:
    """
    @return - Returns the total amount of assets owned by the vault
    """
    total_elastic: uint256 = convert(self.total_asset.elastic, uint256)
    _total_borrow: Rebase = self.total_borrow
    # This could maybe revert in the case of bad debt, is that desired?
    total_interest: uint256 = convert(
        _total_borrow.elastic - _total_borrow.base, uint256
    )  # Interest is the difference between elastic and base, since they start at 1:1
    return total_interest + total_elastic


@view
@external
def convertToAssets(shareAmount: uint256) -> uint256:
    """
    @param shareAmount - The amount of shares to convert to assets
    @return - Returns the amount of assets returned given the amount of shares
    """
    return self._convertToAssets(shareAmount)


@view
@internal
def _convertToAssets(shareAmount: uint256) -> uint256:
    _total_asset: Rebase = self.total_asset
    if _total_asset.base == 0:
        # Shares mint 1:1 at the start until interest accrues
        return shareAmount
    all_share: uint256 = convert(
        _total_asset.elastic + self.total_borrow.elastic, uint256
    )
    return shareAmount * all_share / convert(_total_asset.base, uint256)


@view
@external
def convertToShares(assetAmount: uint256) -> uint256:
    """
    @param assetAmount - The amount of assets to convert to shares
    @return - Returns the amount of shares returned given the amount of assets
    """
    return self._convertToShares(assetAmount)


@view
@internal
def _convertToShares(assetAmount: uint256) -> uint256:
    total_asset_base: uint256 = convert(self.total_asset.base, uint256)
    all_share: uint256 = convert(
        self.total_asset.elastic + self.total_borrow.elastic, uint256
    )
    if all_share == 0:
        # Shares mint 1:1 at the start until interest accrues
        return assetAmount
    return assetAmount * total_asset_base / all_share


@view
@external
def maxDeposit(receiver: address) -> uint256:
    """
    @param receiver - The address of the receiver
    @return - Returns the maximum amount of assets that can be deposited into the vault
    @notice - While technically there is no deposit cap, at unreasonably large uint256 values this may revert
    """
    return max_value(uint256)


@view
@external
def previewDeposit(assets: uint256) -> uint256:
    """
    @param assets - The amount of assets to deposit
    @return - Returns the amount of shares that would be minted if the assets were deposited
    """
    return self._convertToShares(assets)


@external
def deposit(assets: uint256, receiver: address = msg.sender) -> uint256:
    """
    @param assets - The amount of assets to deposit
    @param receiver - The address of the receiver

    @return - Returns the amount of shares minted for the deposit
    """
    self._isPaused()
    shares_out: uint256 = self._add_asset(receiver, assets)
    log Deposit(msg.sender, receiver, assets, shares_out)

    return shares_out


@view
@external
def maxMint(owner: address) -> uint256:
    """
    @notice no cap on max amount of shares to mint except at unreasonably high uint256 values
    """
    return max_value(uint256)


@view
@external
def previewMint(shares: uint256) -> uint256:
    """
    @param shares - The amount of shares to mint
    @return - Returns the amount of assets required to mint the specified amount of shares
    """
    # Convert shares to assets
    return self._convertToAssets(shares)


@external
def mint(shares: uint256, receiver: address = msg.sender) -> uint256:
    """
    @param shares - The amount of shares to mint
    @param receiver - The address of the receiver

    @return - The amount of assets used
    """
    self._isPaused()
    tokens_to_deposit: uint256 = self._convertToAssets(shares)
    shares_out: uint256 = self._add_asset(receiver, tokens_to_deposit)
    log Deposit(msg.sender, receiver, tokens_to_deposit, shares_out)

    return tokens_to_deposit


@view
@external
def maxWithdraw(owner: address) -> uint256:
    """
    @param owner - The address of the owner
    @return - Returns the maximum amount of assets that can be withdrawn from the vault
    """
    return min(
        self._convertToAssets(self.balanceOf[owner]),
        ERC20(asset).balanceOf(self),
    )


@view
@external
def previewWithdraw(assets: uint256) -> uint256:
    """
    @param assets - The amount of assets to withdraw
    @return - The amount of shares worth withdrawn
    @notice - Will revert if you try to preview withdrawing more assets than available currently in the vault's balance
    """
    return min(self._convertToShares(assets), ERC20(asset).balanceOf(self))


@external
def withdraw(
    assets: uint256, receiver: address = msg.sender, owner: address = msg.sender
) -> uint256:
    """
    @param assets - The amount of assets to withdraw
    @param receiver - Reciever of the assets withdrawn
    @param owner - The owners whose assets should be withdrawn

    @return - The amount of shares burned
    """
    self._accrue()
    shares_to_withdraw: uint256 = self._convertToShares(assets)
    shares: uint256 = self._remove_asset(receiver, owner, shares_to_withdraw)
    log Withdraw(msg.sender, receiver, owner, assets, shares)

    return shares


@view
@external
def maxRedeem(owner: address) -> uint256:
    """
    @param owner - The address of the owner
    @return - Returns the maximum amount of shares that can be redeemed from the vault by the owner
    """
    return min(
        self.balanceOf[owner],
        self._convertToShares(ERC20(asset).balanceOf(self)),
    )


@view
@external
def previewRedeem(shares: uint256) -> uint256:
    """
    @param shares - The amount of shares to redeem
    @return - Returns the amount of assets that would be returned if the shares were redeemed
    """
    return min(
        self._convertToAssets(shares),
        self._convertToShares(ERC20(asset).balanceOf(self)),
    )


@external
def redeem(
    shares: uint256, receiver: address = msg.sender, owner: address = msg.sender
) -> uint256:
    """
    @param shares - The amount of shares to redeem
    @param receiver - The address of the receiver
    @param owner - The address of the owner

    @return - The amount of assets returned
    """
    self._accrue()
    assets_out: uint256 = self._convertToAssets(
        self._remove_asset(receiver, owner, shares)
    )
    log Withdraw(msg.sender, receiver, owner, assets_out, shares)

    return assets_out


# ///////////////////////////////////////////////////// #
# 		        Internal Implementations	         	#
# ///////////////////////////////////////////////////// #
@internal
def _isPaused():
    assert (not self.paused)


@internal
def _accrue():
    _accrue_info: AccrueInfo = self.accrue_info
    elapsed_time: uint256 = block.timestamp - convert(
        _accrue_info.last_accrued, uint256
    )
    if elapsed_time == 0:
        # Prevents re-executing this logic if multiple actions are taken in the same block
        return

    _accrue_info.last_accrued = convert(block.timestamp, uint64)

    _total_borrow: Rebase = self.total_borrow
    if _total_borrow.base == 0:
        # If there are no outstanding borrows, there is no need to accrue interest, and interest
        # rate should be moved to minimum to encourage borrowing
        if _accrue_info.interest_per_second != STARTING_INTEREST_PER_SECOND:
            _accrue_info.interest_per_second = STARTING_INTEREST_PER_SECOND
        self.accrue_info = _accrue_info
        return

    interest_accrued: uint256 = 0
    fee_fraction: uint256 = 0
    _total_asset: Rebase = self.total_asset

    # Accrue interest
    interest_accrued = (
        convert(_total_borrow.elastic, uint256)
        * convert(_accrue_info.interest_per_second, uint256)
        * elapsed_time
        / 1000000000000000000
    )  # 1e18, or the divisor for interest per second

    _total_borrow.elastic = _total_borrow.elastic + convert(
        interest_accrued, uint128
    )

    full_asset_amount: uint256 = convert(
        _total_asset.elastic, uint256
    ) + convert(_total_borrow.elastic, uint256)

    # Calculate fees
    fee_amount: uint256 = (
        interest_accrued * self.protocol_fee / PROTOCOL_FEE_DIVISOR
    )  # % of interest paid goes to fee

    fee_fraction = (
        fee_amount * convert(_total_asset.base, uint256) / full_asset_amount
    )  # Update total fees earned
    _accrue_info.fees_earned_fraction = (
        _accrue_info.fees_earned_fraction + convert(fee_fraction, uint128)
    )

    # Fees should be considered in total assets
    self.total_asset.base = _total_asset.base + convert(fee_fraction, uint128)

    # Write new total borrow state to storage
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
        new_interest_per_second: uint64 = convert(
            convert(_accrue_info.interest_per_second, uint256)
            * INTEREST_ELASTICITY
            / scale,
            uint64,
        )
        _accrue_info.interest_per_second = new_interest_per_second

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
        new_interest_per_second: uint64 = convert(
            convert(_accrue_info.interest_per_second, uint256)
            * scale
            / INTEREST_ELASTICITY,
            uint64,
        )

        if new_interest_per_second > MAXIMUM_INTEREST_PER_SECOND:
            _accrue_info.interest_per_second = (
                MAXIMUM_INTEREST_PER_SECOND  # 100% APR maximum
            )

        _accrue_info.interest_per_second = new_interest_per_second

    self.check_surge(_accrue_info)

    self.accrue_info = _accrue_info

@internal
def check_surge(_accrue_info: AccrueInfo):
    dt: uint64 = (
        convert(block.timestamp, uint64) - self.surge_info.last_elapsed_time
    )
    if dt > 86400:
        # if interest rate is increasing
        if (
            _accrue_info.interest_per_second
            > self.surge_info.last_interest_per_second
        ):
            # If daily change in interest rate is greater than Surge threshold, trigger surge breaker
            dr: uint64 = (
                _accrue_info.interest_per_second
                - self.surge_info.last_interest_per_second
            )
            if dr > PROTOCOL_SURGE_THRESHOLD:
                self.surge_info.last_elapsed_time = convert(
                    block.timestamp, uint64
                )
                self.surge_info.last_interest_per_second = (
                    _accrue_info.interest_per_second
                )
                # PoL Should accrue here, instead of to lenders, to discourage pid attacks as described in https://gauntlet.network/reports/pid
                self.protocol_fee = PROTOCOL_FEE_DIVISOR  # 100% Protocol Fee
        else:
            # Reset protocol fee elsewise
            self.protocol_fee = self.DEFAULT_PROTOCOL_FEE  # 10% Protocol Fee

@internal
def _add_collateral(to: address, amount: uint256):
    """
    @param to The address to add collateral for
    @param amount The amount of collateral to add, in tokens
    """
    new_collateral_share: uint256 = self.user_collateral_share[to] + amount
    self.user_collateral_share[to] = new_collateral_share
    old_total_collateral_share: uint256 = self.total_collateral_share
    self.total_collateral_share = old_total_collateral_share + amount
    assert ERC20(collateral).transferFrom(
        msg.sender, self, amount, default_return_value=True
    )  # dev: Transfer Failed

    log AddCollateral(to, amount, new_collateral_share)


@internal
def _remove_collateral(to: address, amount: uint256):
    """
    @param to The address to remove collateral for
    @param amount The amount of collateral to remove, in tokens
    """
    new_collateral_share: uint256 = self.user_collateral_share[to] - amount
    self.user_collateral_share[msg.sender] = new_collateral_share
    self.total_collateral_share = self.total_collateral_share - amount
    assert ERC20(collateral).transfer(
        to, amount, default_return_value=True
    )  # dev: Transfer Failed

    log RemoveCollateral(to, amount, new_collateral_share)


@internal
def _add_asset(to: address, amount: uint256) -> uint256:
    """
    @param to The address to add asset for
    @param amount The amount of asset to add, in tokens
    @return The amount of shares minted
    """
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

    new_balance: uint256 = self.balanceOf[to] + fraction
    self.balanceOf[to] = new_balance

    assert ERC20(asset).transferFrom(
        msg.sender, self, amount, default_return_value=True
    )  # dev: Transfer Failed

    return fraction


@internal
def _remove_asset(to: address, owner: address, amount: uint256) -> uint256:
    """
    @param to The address to remove asset for
    @param amount The amount of asset to remove, in tokens
    @return The amount of shares burned
    """
    if owner != msg.sender:
        assert (
            self.allowance[owner][msg.sender] >= amount
        ), "Insufficient Allowance"
        self.allowance[owner][msg.sender] -= amount

    _total_asset: Rebase = self.total_asset
    all_share: uint256 = convert(
        _total_asset.elastic + self.total_borrow.elastic, uint256
    )
    share: uint256 = (amount * all_share) / convert(_total_asset.base, uint256)

    _total_asset.elastic -= convert(amount, uint128)
    _total_asset.base -= convert(amount, uint128)
    assert _total_asset.base >= 1000, "Below Minimum"
    self.total_asset = _total_asset

    new_balance: uint256 = self.balanceOf[owner] - amount
    self.balanceOf[owner] = new_balance
    assert ERC20(asset).transfer(
        to, amount, default_return_value=True
    )  # dev: Transfer Failed

    return share


@internal
def _update_exchange_rate() -> (bool, uint256):
    """
    @return A tuple of (updated, rate)
        updated: Whether the exchange rate was updated
        rate: The exchange rate
    """
    updated: bool = False
    rate: uint256 = 0

    updated, rate = IOracle(oracle).get()

    if updated:
        self.exchange_rate = rate
    else:
        rate = self.exchange_rate

    return (updated, rate)


@internal
def _borrow(to: address, amount: uint256) -> uint256:
    """
    @param to: The address to send the borrowed tokens to
    @param amount: The amount of asset to borrow, in tokens
    @return: The amount of tokens borrowed
    """
    self._update_exchange_rate()
    fee_amount: uint256 = (
        amount * self.BORROW_OPENING_FEE
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
    _total_asset.elastic = convert(
        convert(_total_asset.elastic, uint256) - amount, uint128
    )
    self.total_asset = _total_asset
    assert ERC20(asset).transfer(
        to, amount, default_return_value=True
    )  # dev: Transfer Failed
    return amount


@internal
def _repay(to: address, payment: uint256) -> uint256:
    """
    @param to: The address to repay the tokens for
    @param payment: The amount of asset to repay, in tokens
    @return: The amount of tokens repaid in shares
    """
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
    assert ERC20(asset).transferFrom(
        msg.sender, self, payment, default_return_value=True
    )  # dev: Transfer Failed

    self.total_asset.elastic = total_share + convert(amount, uint128)
    return amount


@internal
def _is_solvent(user: address, exchange_rate: uint256) -> bool:
    """
    @param user: The user to check
    @param exchange_rate: The exchange rate to use
    @return: Whether the user is solvent
    """
    borrow_part: uint256 = self.user_borrow_part[user]
    if borrow_part == 0:
        return True
    collateral_share: uint256 = self.user_collateral_share[user]
    if collateral_share == 0:
        return False

    _total_borrow: Rebase = self.total_borrow
    collateral_amt: uint256 = (
        (
            collateral_share
            * (EXCHANGE_RATE_PRECISION / COLLATERIZATION_RATE_PRECISION)
        )
        * COLLATERIZATION_RATE
    )

    borrow_part = self.user_borrow_part[user]
    borrow_part = self.mul_div(
        (borrow_part * convert(_total_borrow.elastic, uint256)),
        exchange_rate,
        convert(_total_borrow.base, uint256),
        False,
    )

    return collateral_amt >= borrow_part


# ///////////////////////////////////////////////////// #
# 				External Implementations				#
# ///////////////////////////////////////////////////// #
@external
def __init__(_asset: address, _collateral: address, _oracle: address):
    assert (
        _collateral != 0x0000000000000000000000000000000000000000
    ), "Invalid Collateral"
    collateral = _collateral
    asset = _asset
    oracle = _oracle
    self.DEFAULT_PROTOCOL_FEE = 100000
    self.protocol_fee = 100000  # 10%
    hashed_name: bytes32 = keccak256(convert(NAME, Bytes[50]))
    hashed_version: bytes32 = keccak256(convert("1", Bytes[20]))
    type_hash: bytes32 = keccak256(
        convert(
            "EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)",
            Bytes[82],
        )
    )
    _HASHED_NAME = hashed_name
    _HASHED_VERSION = hashed_version
    _TYPE_HASH = type_hash
    _CACHED_CHAIN_ID = chain.id
    _CACHED_SELF = self
    _CACHED_DOMAIN_SEPARATOR = self._build_domain_separator(
        type_hash, hashed_name, hashed_version
    )
    self.protocol_fee = self.DEFAULT_PROTOCOL_FEE  # 10%
    self.BORROW_OPENING_FEE = 50
    factory = msg.sender


@external
def accrue():
    """
    @dev Accrues interest and updates the exchange rate if needed
    """
    self._accrue()


@external
def add_collateral(to: address, amount: uint256):
    """
    @param to The address to add collateral for
    @param amount The amount of collateral to add, in tokens
    """
    self._accrue()
    self._add_collateral(to, amount)


@external
def remove_collateral(to: address, amount: uint256):
    """
    @param to The address to remove collateral for
    @param amount The amount of collateral to remove, in tokens
    """
    self._accrue()
    self._remove_collateral(to, amount)
    assert self._is_solvent(
        msg.sender, self.exchange_rate
    ), "Insufficient Collateral"


@external
def borrow(to: address, amount: uint256) -> uint256:
    """
    @param to The address to send the borrowed tokens to
    @param amount The amount of asset to borrow, in tokens
    @return The amount of tokens borrowed
    """
    self._isPaused()
    self._accrue()
    borrowed: uint256 = self._borrow(to, amount)
    self.check_surge(self.accrue_info)
    assert self._is_solvent(
        msg.sender, self.exchange_rate
    ), "Insufficient Collateral"
    return borrowed


@external
def repay(to: address, payment: uint256) -> uint256:
    """
    @param to The address to repay the tokens for
    @param payment The amount of asset to repay, in tokens
    @return The amount of tokens repaid in shares
    """
    self._accrue()
    return self._repay(to, payment)


@external
def get_exchange_rate() -> (bool, uint256):
    """
    @return A tuple of (updated, rate)
        updated Whether the exchange rate was updated
        rate The exchange rate
    """
    return self._update_exchange_rate()


@external
def liquidate(user: address, maxBorrowParts: uint256, to: address):
    """
    @param user The user to liquidate
    @param maxBorrowParts The parts to liquidate
    @param to The address to send the liquidated tokens to
    """
    exchange_rate: uint256 = 0
    updated: bool = False  # Never used
    updated, exchange_rate = self._update_exchange_rate()
    self._accrue()

    all_collateral_share: uint256 = 0
    all_borrow_amount: uint256 = 0
    all_borrow_part: uint256 = 0
    _total_borrow: Rebase = self.total_borrow

    if not self._is_solvent(user, exchange_rate):
        available_borrow_part: uint256 = self.user_borrow_part[user]
        borrow_part: uint256 = min(maxBorrowParts, available_borrow_part)
        self.user_borrow_part[user] = available_borrow_part - borrow_part

        borrow_amount: uint256 = self.to_elastic(
            _total_borrow, borrow_part, False
        )

        collateral_share: uint256 = (
            (borrow_amount * LIQUIDATION_MULTIPLIER * exchange_rate)
            / (LIQUIDATION_MULTIPLIER_PRECISION * EXCHANGE_RATE_PRECISION)
        )

        self.user_collateral_share[user] = (
            self.user_collateral_share[user] - collateral_share
        )

        all_collateral_share += collateral_share
        all_borrow_amount += borrow_amount
        all_borrow_part += borrow_part

    assert all_borrow_amount != 0, "CogPair: all are solvent"

    self.total_borrow.elastic = self.total_borrow.elastic - convert(
        all_borrow_amount, uint128
    )
    self.total_borrow.base = self.total_borrow.base - convert(
        all_borrow_part, uint128
    )

    self.total_collateral_share = (
        self.total_collateral_share - all_collateral_share
    )

    assert ERC20(collateral).transfer(
        to, all_collateral_share, default_return_value=True
    )  # dev: Transfer failed

    assert ERC20(asset).transferFrom(
        msg.sender, self, all_borrow_part, default_return_value=True
    )  # dev: Transfer failed

    self.total_asset.elastic = self.total_asset.elastic + convert(
        all_borrow_part, uint128
    )


# ///////////////////////////////////////////////////// #
# 				Tinkermaster Control Panel				#
# ///////////////////////////////////////////////////// #

@external
def update_borrow_fee(newFee: uint256):
    assert (msg.sender == factory)
    assert (
        newFee <= BORROW_OPENING_FEE_PRECISION / 2
    )  # Prevent rugging via borrow fee
    self.BORROW_OPENING_FEE = newFee


@external
def update_default_protocol_fee(newFee: uint256):
    assert (msg.sender == factory)
    assert (newFee <= PROTOCOL_FEE_DIVISOR)
    self.DEFAULT_PROTOCOL_FEE = newFee


@external
def pause():
    assert (msg.sender == factory)
    self.paused = True


@external
def unpause():
    assert (msg.sender == factory)
    self.paused = False


@external
def roll_over_pol():
    """
    @dev Withdraws protocol fees and deposits them into the pool on behalf of the tinkermaster address
    """
    assert (msg.sender == factory)
    _fee_to: address = ICogFactory(factory).fee_to()
    _accrue_info: AccrueInfo = self.accrue_info

    # Withdraw protocol fees
    fees_earned_fraction: uint256 = convert(
        _accrue_info.fees_earned_fraction, uint256
    )
    self.balanceOf[_fee_to] = self.balanceOf[_fee_to] + fees_earned_fraction
    self.accrue_info.fees_earned_fraction = 0

    log Transfer(convert(0, address), _fee_to, fees_earned_fraction)