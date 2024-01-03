import { Address, BigDecimal, BigInt } from '@graphprotocol/graph-ts'
import { Token } from "../../generated/schema"
import { ERC20 } from '../../generated/ERC20'
import { TokenDailySnapshot, TokenHourlySnapshot } from '../../generated/schema'
import { dayFromTimestamp, hourFromTimestamp } from '../utils/dates'

export function createPair(address: Address, timestamp: BigInt): Token {
    const pair = new Pair(address.toHexString())
    pair.timestamp = timestamp
  
    const erc20Token = ERC20.bind(address)
    pair.name = erc20Token.name()
    pair.symbol = erc20Token.symbol()
    pair.decimals = erc20Token.decimals()
    pair.save()
  
    return pair
  }

  export function getOrCreatePair(address: Address, timestamp: BigInt): Pair {
    let pair = Pair.load(address.toHexString())

    if (pair === null) {
      pair = createPair(address, timestamp)
    } else {
      updatePair(pair, timestamp)
    }
  
    return pair
  }
  
  export function getPair(address: string): Pair {
    let pair = Pair.load(address) as Pair
  
    return pair
  }

  export function handleMediumPairCreated(Event: PairCreatedEvent): void {
    let entity = new mediumPairCreated {
    event.transaction.hash.concatI32(event.logIndex.toI32())
    }
    entity.factory = event.params.factory
    }

    export function handleHighPairCreated(Event: PairCreatedEvent): void {
        let entity = new highPairCreated {
        event.transaction.hash.concatI32(event.logIndex.toI32())
        }
        entity.factory = event.params.factory
        }