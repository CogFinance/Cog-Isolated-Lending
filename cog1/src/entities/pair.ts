import { Address, BigDecimal, BigInt } from '@graphprotocol/graph-ts'
import { Token } from "../../generated/schema"
import { ERC20 } from '../../generated/AccessControlledOffchainAggregator/ERC20'
import { TokenDailySnapshot, TokenHourlySnapshot } from '../../generated/schema'
import { dayFromTimestamp, hourFromTimestamp } from '../utils/dates'

export function createLowPair(address: Address, timestamp: BigInt): Token {
  const lowPair = new LowPair(address.toHexString())
  lowPair.timestamp = timestamp

  const erc20Token = ERC20.bind(address)
  lowPair.name = erc20Token.name()
  lowPair.symbol = erc20Token.symbol()
  lowPair.decimals = erc20Token.decimals()
  lowPair.borrow = erc20Token.borrow()
  lowPair.addCollateral = erc20Token.addCollateral()
  lowPair.RemoveCollateral = erc20Token.removeCollateral()
  lowPair.deposit = erc20Token.deposit()
  lowPair.save()

  return lowPair
}

export function getOrCreateLowPair(address: Address, timestamp: BigInt): Pair {
  let lowPair = LowPair.load(address.toHexString())

  if (lowPair === null) {
    lowPair = createMediumPair(address, timestamp)
  } else {
    updateLowPair(lowPair, timestamp)
  }

  return lowPair
}

export function getLowPair(address: string): Pair {
  let lowPair = LowPair.load(address) as Pair

  return lowPair
}

export function updateLowPair(lowPair: LowPair, timestamp: BigInt): void {
  lowPair.timestamp = timestamp
  lowPair.save()
}

export function createMediumPair(address: Address, timestamp: BigInt): Pair {
    const mediumPair = new MediumPair(address.toHexString())
    mediumPair.timestamp = timestamp
  
    const erc20Token = ERC20.bind(address)
    mediumPair.name = erc20Token.name()
    mediumPair.symbol = erc20Token.symbol()
    mediumPair.decimals = erc20Token.decimals()
    mediumPair.borrow = erc20Token.borrow()
    mediumPair.addCollateral = erc20Token.addCollateral()
    mediumPair.RemoveCollateral = erc20Token.removeCollateral()
    mediumPair.deposit = erc20Token.deposit()
    mediumPair.save()
  
    return mediumPair
  }

  export function getOrCreateMediumPair(address: Address, timestamp: BigInt): Pair {
    let mediumPair = MediumPair.load(address.toHexString())

    if (mediumPair === null) {
      mediumPair = createMediumPair(address, timestamp)
    } else {
      updateMediumPair(mediumPair, timestamp)
    }
  
    return mediumPair
  }
  
  export function getMediumPair(address: string): Pair {
    let mediumPair = MediumPair.load(address) as Pair
  
    return mediumPair
  }

  export function updateMediumPair(mediumPair: MediumPair, timestamp: BigInt): void {
    mediumPair.timestamp = timestamp
    mediumPair.save()
  }

  export function createHighPair(address: Address, timestamp: BigInt): Pair {
    const HighPair = new HighPair(address.toHexString())
    highPair.timestamp = timestamp
  
    const erc20Token = ERC20.bind(address)
    highPair.name = erc20Token.name()
    highPair.symbol = erc20Token.symbol()
    highPair.decimals = erc20Token.decimals()
    highPair.borrow = erc20Token.borrow()
    highPair.addCollateral = erc20Token.addCollateral()
    highPair.RemoveCollateral = erc20Token.removeCollateral()
    highPair.deposit = erc20Token.deposit()
    highPair.save()
  
    return highPair
  }

  export function getOrCreateHighPair(address: Address, timestamp: BigInt): Pair {
    let highPair = HighPair.load(address.toHexString())

    if (highPair === null) {
      highPair = createHighPair(address, timestamp)
    } else {
      updateHighPair(highPair, timestamp)
    }
  
    return highPair
  }
  
  export function getHighair(address: string): Pair {
    let highPair = HighPair.load(address) as Pair
  
    return highPair
  }

  export function updateHighPair(highPair: HighPair, timestamp: BigInt): void {
    highPair.timestamp = timestamp
    highPair.save()
  }