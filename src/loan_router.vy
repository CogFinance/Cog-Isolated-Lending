# @version 0.3.9
"""
@title Loan Router
@author cog.finance
@license AGPL-3.0
@notice A very smol helper contract for routing multiple borrows
"""

from vyper.interfaces import ERC20

interface CogPair:
  # We can omit the `to` parameter because it defaults to msg.sender, which should be the router in this case
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
  for route in path:
    if route.pair != empty(address):
      collateral: address = CogPair(route.pair).collateral()
      asset: address = CogPair(route.pair).asset()

      ERC20(collateral).transferFrom(msg.sender, self, route.collateral_added)
      ERC20(collateral).approve(route.pair, route.collateral_added)
      CogPair(route.pair).add_collateral(msg.sender, route.collateral_added)
 
      CogPair(route.pair).borrow(route.assets_to_borrow, msg.sender, msg.sender)
