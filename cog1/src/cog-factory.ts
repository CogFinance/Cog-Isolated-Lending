import {
    StablePairCreated as StablePairCreatedEvent,
    LowPairCreated as LowPairCreatedEvent,
    MediumPairCreated as MediumPairCreatedEvent,
    HighPairCreated as HighPairCreatedEvent,
  } from "../generated/CogFactory/CogFactory"
  import {
    StablePairCreated,
    LowPairCreated,
    MediumPairCreated,
    HighPairCreated,
  } from "../generated/schema"
    
  export function handleStablePairCreated(event: StablePairCreatedEvent): void {
    let entity = new StablePairCreated(
      event.transaction.hash.concatI32(event.logIndex.toI32())
    )
    entity.asset = event.params.asset
    entity.collateral = event.params.collateral
    entity.pair = event.params.pair

  
    entity.blockNumber = event.block.number
    entity.blockTimestamp = event.block.timestamp
    entity.transactionHash = event.transaction.hash
  
    entity.save()
  }

  export function handleLowPairCreated(event: LowPairCreatedEvent): void {
    let entity = new LowPairCreated(
      event.transaction.hash.concatI32(event.logIndex.toI32())
    )
    entity.asset = event.params.asset
    entity.collateral = event.params.collateral
    entity.pair = event.params.pair
  
    entity.blockNumber = event.block.number
    entity.blockTimestamp = event.block.timestamp
    entity.transactionHash = event.transaction.hash
  
    entity.save()
  }

  export function handleMediumPairCreated(event: MediumPairCreatedEvent): void {
    let entity = new MediumPairCreated(
      event.transaction.hash.concatI32(event.logIndex.toI32())
    )
    entity.asset = event.params.asset
    entity.collateral = event.params.collateral
    entity.pair = event.params.pair

  
    entity.blockNumber = event.block.number
    entity.blockTimestamp = event.block.timestamp
    entity.transactionHash = event.transaction.hash
  
    entity.save()
  }
  
  export function handleHighPairCreated(event: HighPairCreatedEvent): void {
    let entity = new HighPairCreated(
      event.transaction.hash.concatI32(event.logIndex.toI32())
    )
    entity.asset = event.params.asset
    entity.collateral = event.params.collateral
    entity.pair = event.params.pair

  
    entity.blockNumber = event.block.number
    entity.blockTimestamp = event.block.timestamp
    entity.transactionHash = event.transaction.hash
  
    entity.save()
  }
  
  