import { newMockEvent } from "matchstick-as"
import { ethereum, Address, BigInt } from "@graphprotocol/graph-ts"
import {
  AddCollateral,
  RemoveCollateral,
  Borrow,
  Paused,
  UnPaused,
  Transfer,
  Approval,
  Deposit,
  Withdraw
} from "../generated/CogPair/CogPair"

export function createAddCollateralEvent(
  to: Address,
  amount: BigInt,
  user_collateral_share: BigInt
): AddCollateral {
  let addCollateralEvent = changetype<AddCollateral>(newMockEvent())

  addCollateralEvent.parameters = new Array()

  addCollateralEvent.parameters.push(
    new ethereum.EventParam("to", ethereum.Value.fromAddress(to))
  )
  addCollateralEvent.parameters.push(
    new ethereum.EventParam("amount", ethereum.Value.fromUnsignedBigInt(amount))
  )
  addCollateralEvent.parameters.push(
    new ethereum.EventParam(
      "user_collateral_share",
      ethereum.Value.fromUnsignedBigInt(user_collateral_share)
    )
  )

  return addCollateralEvent
}

export function createRemoveCollateralEvent(
  to: Address,
  amount: BigInt,
  user_collateral_share: BigInt
): RemoveCollateral {
  let removeCollateralEvent = changetype<RemoveCollateral>(newMockEvent())

  removeCollateralEvent.parameters = new Array()

  removeCollateralEvent.parameters.push(
    new ethereum.EventParam("to", ethereum.Value.fromAddress(to))
  )
  removeCollateralEvent.parameters.push(
    new ethereum.EventParam("amount", ethereum.Value.fromUnsignedBigInt(amount))
  )
  removeCollateralEvent.parameters.push(
    new ethereum.EventParam(
      "user_collateral_share",
      ethereum.Value.fromUnsignedBigInt(user_collateral_share)
    )
  )

  return removeCollateralEvent
}

export function createBorrowEvent(
  amount: BigInt,
  to: Address,
  _from: Address
): Borrow {
  let borrowEvent = changetype<Borrow>(newMockEvent())

  borrowEvent.parameters = new Array()

  borrowEvent.parameters.push(
    new ethereum.EventParam("amount", ethereum.Value.fromUnsignedBigInt(amount))
  )
  borrowEvent.parameters.push(
    new ethereum.EventParam("to", ethereum.Value.fromAddress(to))
  )
  borrowEvent.parameters.push(
    new ethereum.EventParam("_from", ethereum.Value.fromAddress(_from))
  )

  return borrowEvent
}

export function createPausedEvent(time: BigInt): Paused {
  let pausedEvent = changetype<Paused>(newMockEvent())

  pausedEvent.parameters = new Array()

  pausedEvent.parameters.push(
    new ethereum.EventParam("time", ethereum.Value.fromUnsignedBigInt(time))
  )

  return pausedEvent
}

export function createUnPausedEvent(time: BigInt): UnPaused {
  let unPausedEvent = changetype<UnPaused>(newMockEvent())

  unPausedEvent.parameters = new Array()

  unPausedEvent.parameters.push(
    new ethereum.EventParam("time", ethereum.Value.fromUnsignedBigInt(time))
  )

  return unPausedEvent
}

export function createTransferEvent(
  sender: Address,
  receiver: Address,
  amount: BigInt
): Transfer {
  let transferEvent = changetype<Transfer>(newMockEvent())

  transferEvent.parameters = new Array()

  transferEvent.parameters.push(
    new ethereum.EventParam("sender", ethereum.Value.fromAddress(sender))
  )
  transferEvent.parameters.push(
    new ethereum.EventParam("receiver", ethereum.Value.fromAddress(receiver))
  )
  transferEvent.parameters.push(
    new ethereum.EventParam("amount", ethereum.Value.fromUnsignedBigInt(amount))
  )

  return transferEvent
}

export function createApprovalEvent(
  owner: Address,
  spender: Address,
  allowance: BigInt
): Approval {
  let approvalEvent = changetype<Approval>(newMockEvent())

  approvalEvent.parameters = new Array()

  approvalEvent.parameters.push(
    new ethereum.EventParam("owner", ethereum.Value.fromAddress(owner))
  )
  approvalEvent.parameters.push(
    new ethereum.EventParam("spender", ethereum.Value.fromAddress(spender))
  )
  approvalEvent.parameters.push(
    new ethereum.EventParam(
      "allowance",
      ethereum.Value.fromUnsignedBigInt(allowance)
    )
  )

  return approvalEvent
}

export function createDepositEvent(
  depositor: Address,
  receiver: Address,
  assets: BigInt,
  shares: BigInt
): Deposit {
  let depositEvent = changetype<Deposit>(newMockEvent())

  depositEvent.parameters = new Array()

  depositEvent.parameters.push(
    new ethereum.EventParam("depositor", ethereum.Value.fromAddress(depositor))
  )
  depositEvent.parameters.push(
    new ethereum.EventParam("receiver", ethereum.Value.fromAddress(receiver))
  )
  depositEvent.parameters.push(
    new ethereum.EventParam("assets", ethereum.Value.fromUnsignedBigInt(assets))
  )
  depositEvent.parameters.push(
    new ethereum.EventParam("shares", ethereum.Value.fromUnsignedBigInt(shares))
  )

  return depositEvent
}

export function createWithdrawEvent(
  withdrawer: Address,
  receiver: Address,
  owner: Address,
  assets: BigInt,
  shares: BigInt
): Withdraw {
  let withdrawEvent = changetype<Withdraw>(newMockEvent())

  withdrawEvent.parameters = new Array()

  withdrawEvent.parameters.push(
    new ethereum.EventParam(
      "withdrawer",
      ethereum.Value.fromAddress(withdrawer)
    )
  )
  withdrawEvent.parameters.push(
    new ethereum.EventParam("receiver", ethereum.Value.fromAddress(receiver))
  )
  withdrawEvent.parameters.push(
    new ethereum.EventParam("owner", ethereum.Value.fromAddress(owner))
  )
  withdrawEvent.parameters.push(
    new ethereum.EventParam("assets", ethereum.Value.fromUnsignedBigInt(assets))
  )
  withdrawEvent.parameters.push(
    new ethereum.EventParam("shares", ethereum.Value.fromUnsignedBigInt(shares))
  )

  return withdrawEvent
}
