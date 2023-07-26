# @version 0.3.9
"""
@title Loan Router
@author cog.finance
@license AGPL-3.0
@notice A very smol helper contract for routing multiple borrows
"""

from vyper.interfaces import ERC20

interface CogPair:
  def borrow(amount: uint256, _from: address, to: address) -> uint256 : nonpayable

  def add_collateral(to: address, amount: uint256) : nonpayable

  def collateral() -> address: view
  def asset() -> address: view

struct Hop:
  pair: address
  collateral_added: uint256
  assets_to_borrow: uint256

@external
def loanTokens(path: Hop[5], deadline: uint256):
  assert(block.timestamp < deadline)
  
  # Prefund initial hop
  ERC20(collateral).transferFrom(msg.sender, self, route.collateral_added)

  for index in range(5):
    route: Hop = path[index]
    if route.pair != empty(address):
      collateral: address = CogPair(route.pair).collateral()
      asset: address = CogPair(route.pair).asset()

      ERC20(collateral).approve(route.pair, route.collateral_added)
      CogPair(route.pair).add_collateral(msg.sender, route.collateral_added)
      CogPair(route.pair).borrow(route.assets_to_borrow, msg.sender, self)
    else:
      final_asset: address =  
      ERC20()
      return
