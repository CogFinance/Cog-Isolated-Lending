import { Address, BigDecimal, BigInt, TypedMap } from '@graphprotocol/graph-ts'
import { toDecimal } from './decimals'
import { getTokenPrice } from '../entities/token'
import { BIG_INT_0, BIG_INT_1E18 } from './constants'

const BIG_DECIMAL_0 = BigDecimal.fromString('0');
const USDC_POOL = Address.fromString('0x06eFdBFf2a14a7c8E15944D1F4A48F9F95F663A4');
const STETH_POOL = Address.fromString('0x5300000000000000000000000000000000000004');
const STETH_ORACLE = Address.fromString('0x86392dc19c0b719886221c78ab11eb8cf5c52812');

let oracleLookupTable = new TypedMap<string, Address>()
oracleLookupTable.set(STETH_POOL,STETH_ORACLE)

export function getOracleTokenPriceInUSD(oracleAddress: Address): BigDecimal {
    let oracle = PriceOracle.bind(oracleAddress)
    let price = toDecimal(oracle.latestAnswer(), 8)

    return price
}

export function getTokenPriceInUSD(token: string, timestamp: BigInt | null = null): BigDecimal {
    const oracleAddress = oracleLookupTable.get(token)
    if (oracleAddress) {
        return getOracleTokenPriceInUSD(oracleAddress)    
    }

    return BIG_DECIMAL_0
}

export function getETHPriceInUSD(): BigDecimal {
  let oracle = PriceOracle.bind(STETH_ORACLE)
  let price = toDecimal(oracle.latestAnswer(), 8)

  return price
}

export function getUSDCPriceInUSD(): BigDecimal {
    let oracle = PriceOracle.bind(USDC_ORACLE)
    let price = toDecimal(oracle.latestAnswer(), 8)

    return price
}