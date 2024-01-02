import { Address, BigDecimal, BigInt } from '@graphprotocol/graph-ts'
import { Token } from "../../generated/schema"
import { ERC20 } from '../../generated/UniswapV3Pool/ERC20'
import { getTokenPriceInUSD } from '../utils/prices'
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

  }