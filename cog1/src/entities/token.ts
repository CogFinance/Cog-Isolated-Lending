import { Address, BigDecimal, BigInt } from '@graphprotocol/graph-ts'
import { Token } from "../../generated/schema"
import { ERC20 } from '../../generated/UniswapV3Pool/ERC20'
import { getTokenPriceInUSD } from '../utils/prices'
import { TokenDailySnapshot, TokenHourlySnapshot } from '../../generated/schema'
import { dayFromTimestamp, hourFromTimestamp } from '../utils/dates'

export function createToken(address: Address, timestamp: BigInt): Token {
  const token = new Token(address.toHexString())
  token.timestamp = timestamp

  const erc20Token = ERC20.bind(address)
  token.name = erc20Token.name()
  token.symbol = erc20Token.symbol()
  token.decimals = erc20Token.decimals()
  token.price = getTokenPriceInUSD(token.id, timestamp)
  token.save()

  return token
}

export function getOrCreateToken(address: Address, timestamp: BigInt): Token {
  let token = Token.load(address.toHexString())

  if (token === null) {
    token = createToken(address, timestamp)
  } else {
    updateToken(token, timestamp)
  }

  return token
}

export function getToken(address: string): Token {
  let token = Token.load(address) as Token

  return token
}

export function getTokenPrice(address: string): BigDecimal {
  let token = Token.load(address) as Token

  return token.price
}

export function handleSwap(Event: SwapEvent): void {
  let entity = new swap {
  event.transaction.hash.concatI32(event.logIndex.toI32())
  }
  entity.quoter = event.params.quoter
  }

export function updateToken(token: Token, timestamp: BigInt): void {
  token.timestamp = timestamp
  token.price = getTokenPriceInUSD(token.id, timestamp)
  updateOrCreateHourData(token, timestamp)
  updateOrCreateDayData(token, timestamp)
  token.save()
}

export function updateOrCreateDayData(Token: Token, timestamp: BigInt): void {
  const dayTimestamp = dayFromTimestamp(timestamp)
  const dataID = Token.id + '-' + dayTimestamp

  let dayData = TokenDailySnapshot.load(dataID)
  if (dayData === null) {
    dayData = new TokenDailySnapshot(dataID)
    dayData.timeframe = BigInt.fromString(dayTimestamp)
  }

  dayData.Token = Token.id
  dayData.timestamp = timestamp
  dayData.name = Token.name
  dayData.symbol = Token.symbol
  dayData.decimals = Token.decimals
  dayData.price = Token.price
  dayData.save()
}

export function updateOrCreateHourData(Token: Token, timestamp: BigInt): void {
  const hourTimestamp = hourFromTimestamp(timestamp)
  const dataID = Token.id + '-' + hourTimestamp

  let hourData = TokenHourlySnapshot.load(dataID)
  if (hourData === null) {
    hourData = new TokenHourlySnapshot(dataID)
    hourData.timeframe = BigInt.fromString(hourTimestamp)
  }

  hourData.Token = Token.id
  hourData.timestamp = timestamp
  hourData.name = Token.name
  hourData.symbol = Token.symbol
  hourData.decimals = Token.decimals
  hourData.price = Token.price
  hourData.save()
}