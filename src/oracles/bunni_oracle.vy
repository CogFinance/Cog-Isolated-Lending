# @version 0.3.9

# Empty IUniswapV3Pool interface
interface IUniswapV3Pool:
    def factory() -> address: view #Not used

# BunniToken Interface
interface IBunniToken:
    def pool() -> IUniswapV3Pool: view
    def tickLower() -> int24: view
    def tickUpper() -> int24: view

# BunniLens Interface
interface IBunniLens:
    def pricePerFullShare(key: BunniKey) -> (uint128, uint256, uint256): view

# Oracle Interface
interface IOracle:
    def get() -> (bool, uint256): nonpayable
    def peek() -> (bool, uint256): view
    def peekSpot() -> uint256: view
    def symbol() -> String[1]: view
    def name() -> String[1]: view

implements: IOracle

# BunniKey struct
struct BunniKey:
    pool: IUniswapV3Pool
    tickLower: int24
    tickUpper: int24

bunny_lens: public(IBunniLens)
bunni_token: public(address)
bunni_key: public(BunniKey)
asset_0_oracle: public(IOracle)
asset_1_oracle: public(IOracle)


@external
def __init__(_bunny_lens: address, _bunni_token: address, _asset_0_oracle: address, _asset_1_oracle: address):
    pool: IUniswapV3Pool = IBunniToken(_bunni_token).pool()
    tickLower: int24 = IBunniToken(_bunni_token).tickLower()
    tickUpper: int24 = IBunniToken(_bunni_token).tickUpper()

    self.bunni_key = BunniKey({pool: pool, tickLower: tickLower, tickUpper: tickUpper})
    self.bunny_lens = IBunniLens(_bunny_lens)
    self.bunni_token = _bunni_token
    self.asset_0_oracle = IOracle(_asset_0_oracle)
    self.asset_1_oracle = IOracle(_asset_1_oracle)


@view
@internal
def _get_final_rate(rate_0: uint256, rate_1: uint256) -> uint256:
    _: uint128 = 0
    amount_0: uint256 = 0
    amount_1: uint256 = 0

    (_, amount_0, amount_1) = self.bunny_lens.pricePerFullShare(self.bunni_key)

    return  amount_0 * rate_0 + amount_1 * rate_1


@external
def get() -> (bool, uint256):
    success_0: bool = False
    success_1: bool = False
    rate_0: uint256 = 0
    rate_1: uint256 = 0

    (success_0, rate_0) = self.asset_0_oracle.get()
    (success_1, rate_1) = self.asset_1_oracle.get()

    final_rate: uint256 = self._get_final_rate(rate_0, rate_1)
    return (success_0 and success_1, final_rate)


@view
@external
def peek() -> (bool, uint256):
    success_0: bool = False
    success_1: bool = False
    rate_0: uint256 = 0
    rate_1: uint256 = 0

    (success_0, rate_0) = self.asset_0_oracle.peek()
    (success_1, rate_1) = self.asset_1_oracle.peek()

    final_rate: uint256 = self._get_final_rate(rate_0, rate_1)
    return (success_0 and success_1, final_rate)


@view
@external
def peekSpot() -> uint256:
    rate_0: uint256 = 0
    rate_1: uint256 = 0

    rate_0 = self.asset_0_oracle.peekSpot()
    rate_1 = self.asset_1_oracle.peekSpot()

    final_rate: uint256 = self._get_final_rate(rate_0, rate_1)
    return final_rate


@view
@external
def symbol() -> String[5]:
    return "BUNNI"


@view
@external
def name() -> String[5]:
    return "Bunni"