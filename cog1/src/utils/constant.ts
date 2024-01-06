import { Address, BigDecimal, BigInt, Bytes } from '@graphprotocol/graph-ts';


export const BIG_INT_1E18 = BigInt.fromString('1000000000000000000');
export const BIG_INT_1E7 = BigInt.fromString('10000000');
export const BIG_INT_0 = BigInt.fromI32(0);
export const BIG_INT_1 = BigInt.fromI32(1);
export const CACHE_INTERVAL = BigInt.fromI32(600); // 10 minutes

export const BIG_DECIMAL_1E18 = BigDecimal.fromString('1e18');
export const BIG_DECIMAL_1E8 = BigDecimal.fromString('1e8');
export const BIG_DECIMAL_1E7 = BigDecimal.fromString('1e7');
export const BIG_DECIMAL_1E4 = BigDecimal.fromString('1e4');
export const BIG_DECIMAL_100 = BigDecimal.fromString('100');
export const BIG_DECIMAL_2 = BigDecimal.fromString('2');
export const BIG_DECIMAL_1 = BigDecimal.fromString('1');
export const BIG_DECIMAL_0 = BigDecimal.fromString('0');
export const BIG_DECIMAL_MIN_1 = BigDecimal.fromString('-1');
export const BIG_DECIMAL_YEAR = BigDecimal.fromString('31536000');
export const ZERO_ADDRESS = Address.fromHexString('0x0000000000000000000000000000000000000000');

export const USDC_TOKEN = Address.fromString('0x06eFdBFf2a14a7c8E15944D1F4A48F9F95F663A4');
export const WETH_TOKEN = Address.fromString('0x5300000000000000000000000000000000000004');
export const CRV_TOKEN = Address.fromString('0xB755039eDc7910C1F1BD985D48322E55A31AC0bF');
export const AAVE_TOKEN = Address.fromString('0x79379c0e09a41d7978f883a56246290ee9a8c4d3');
export const WSTETH_TOKEN = Address.fromString('0xf610A9dfB7C89644979b4A0f27063E9e7d7Cda32');
export const RETH_TOKEN = Address.fromString('0x53878B874283351D26d206FA512aEcE1Bef6C0dD');