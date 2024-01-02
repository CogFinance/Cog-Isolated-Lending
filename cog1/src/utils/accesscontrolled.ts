import {
    AnswerUpdated as AnswerUpdatedEvent,
  } from "../generated/AccessControlledOffchainAggregator/AccessControlledOffchainAggregator"
  import {
    AnswerUpdated,
  } from "../generated/schema"
  
  export function handleAnswerUpdated(event: AnswerUpdatedEvent): void {
    let entity = new AnswerUpdated(
      event.transaction.hash.concatI32(event.logIndex.toI32())
    )
    entity.current = event.params.current
    entity.roundId = event.params.roundId
    entity.updatedAt = event.params.updatedAt
  
    entity.blockNumber = event.block.number
    entity.blockTimestamp = event.block.timestamp
    entity.transactionHash = event.transaction.hash
  
    entity.save()
  }