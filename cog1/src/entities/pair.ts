import { Address, BigDecimal, BigInt } from '@graphprotocol/graph-ts'
import { Token } from "../../generated/schema"
import { ERC20 } from '../../generated/UniswapV3Pool/ERC20'
import { getTokenPriceInUSD } from '../utils/prices'
import { TokenDailySnapshot, TokenHourlySnapshot } from '../../generated/schema'
import { dayFromTimestamp, hourFromTimestamp } from '../utils/dates'

export function createPair(address: Address, timestamp: BigInt): Token {
    const pair = new Pair(address.toHexString())
    token.timestamp = timestamp
  
    const erc20Token = ERC20.bind(address)
    token.name = erc20Token.name()
    token.symbol = erc20Token.symbol()
    token.decimals = erc20Token.decimals()
    token.price = getTokenPriceInUSD(token.id, timestamp)
    token.save()
  
    return token
  }