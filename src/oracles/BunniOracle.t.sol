pragma solidity 0.8.19;

//import "./../interfaces/IOracle.sol";
import "./BunniOracle.sol";
import { Vm } from "forge-std/Vm.sol";
import { Test } from "forge-std/Test.sol";

interface IERC20 {
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
    function totalSupply() external view returns (uint256);
    function balanceOf(address account) external view returns (uint256);
    function transfer(address to, uint256 value) external returns (bool);
    function allowance(address owner, address spender) external view returns (uint256);
    function approve(address spender, uint256 value) external returns (bool);
    function transferFrom(address from, address to, uint256 value) external returns (bool);
    function mint(address to, uint256 amount) external;
}

//UniswapV3Pool interface
interface IUniswapPool {
  function swap(
    address recipient,
    bool zeroForOne,
    int256 amountSpecified,
    uint160 sqrtPriceLimitX96,
    bytes memory data
  ) external returns (int256 amount0, int256 amount1);
  function token0() external view returns (address);
  function token1() external view returns (address);
}

interface IBunniTkn {
    function pool() external view returns (IUniswapPool);
}

interface IBunniOracle {
    function bunni_key() external view returns(BunniKey memory);
}

interface chainlinkAggregatorV3Interface {
  function latestRoundData() external view returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound);
  function decimals() external view returns (uint8);
}

contract BunniOracleTest is Test {
  //BUNNI
  address bunniLens = 0xb73F303472C4fD4FF3B9f59ce0F9b13E47fbfD19;

  //USDC/WETH
  IOracle usdc_weth_bunniOracle;
  IUniswapPool usdc_weth_pool;
  address usdc_weth_bunniToken = 0x680026A1C99a1eC9878431F730706810bFac9f31; //USDC/WETH LP bunni token
  uint256 bunni_USDC_WETH_Price;

  //DAI/USDC
  IOracle dai_usdc_bunniOracle;
  IUniswapPool dai_usdc_pool;
  address dai_usdc_bunniToken = 0xC962Df6E0A931913B1a1D75E91299153A9D839b8; //DAI/USDC LP bunni token
  uint256 bunni_DAI_USDC_Price;

  //rETH/WETH
  IOracle reth_weth_bunniOracle;
  IUniswapPool reth_weth_pool;
  address reth_weth_bunniToken = 0x55Dcf951f9009425aAfE8Bfca348577451ACB433; //rETH/WETH LP bunni token
  uint256 bunni_rETH_WETH_Price;
  
  //Cog Oracles
  address usdc_oracle = address(0xa0);
  address weth_oracle = address(0xa1);
  address dai_oracle = address(0xa2);
  address reth_oracle = address(0xa3);

  //Chainlink Oracles
  address chainlink_USDC_ETH_Oracle = 0x986b5E1e1755e3C2440e960477f25201B0a8bbD4;
  address chainlink_DAI_ETH_Oracle = 0x773616E4d11A78F511299002da57A0a94577F1f4;
  address chainlink_rETH_ETH_Oracle = 0x536218f9E9Eb48863970252233c8F271f554C2d0;

  //Utils
  IUniswapPool currentPool;
  uint160 constant UNI_V3_SLIPPAGE = 7 * 10 ** 45;

  function setUp() public {
    //fork mainnet
    {
      uint256 ethId = vm.createFork("https://eth.llamarpc.com");
      vm.selectFork(ethId);
      vm.rollFork(18422679);
    }

    //get pool addresses
    usdc_weth_pool = IBunniTkn(usdc_weth_bunniToken).pool();
    dai_usdc_pool = IBunniTkn(dai_usdc_bunniToken).pool();
    reth_weth_pool = IBunniTkn(reth_weth_bunniToken).pool();

    //mock cog oracles
    uint256 WETH_Price = 10 ** 18; //in wei
    vm.mockCall(
        weth_oracle,
        abi.encodeWithSelector(IOracle.get.selector),
        abi.encode(true, WETH_Price)
    );
    vm.mockCall(
        weth_oracle,
        abi.encodeWithSelector(IOracle.peek.selector),
        abi.encode(true, WETH_Price)
    );
    vm.mockCall(
        weth_oracle,
        abi.encodeWithSelector(IOracle.peekSpot.selector),
        abi.encode(WETH_Price)
    );

    (,int256 usdc_price,,,) = chainlinkAggregatorV3Interface(chainlink_USDC_ETH_Oracle).latestRoundData();
    uint256 chainlink_USDC_Price = uint256(usdc_price); //in wei
    vm.mockCall(
        usdc_oracle,
        abi.encodeWithSelector(IOracle.get.selector),
        abi.encode(true, chainlink_USDC_Price)
    );
    vm.mockCall(
        usdc_oracle,
        abi.encodeWithSelector(IOracle.peek.selector),
        abi.encode(true, chainlink_USDC_Price)
    );
    vm.mockCall(
        usdc_oracle,
        abi.encodeWithSelector(IOracle.peekSpot.selector),
        abi.encode(chainlink_USDC_Price)
    );

    (,int256 dai_price,,,) = chainlinkAggregatorV3Interface(chainlink_DAI_ETH_Oracle).latestRoundData();
    uint256 chainlink_DAI_Price = uint256(dai_price); //in wei
    vm.mockCall(
        dai_oracle,
        abi.encodeWithSelector(IOracle.get.selector),
        abi.encode(true, chainlink_DAI_Price)
    );
    vm.mockCall(
        dai_oracle,
        abi.encodeWithSelector(IOracle.peek.selector),
        abi.encode(true, chainlink_DAI_Price)
    );
    vm.mockCall(
        dai_oracle,
        abi.encodeWithSelector(IOracle.peekSpot.selector),
        abi.encode(chainlink_DAI_Price)
    );

    (,int256 reth_price,,,) = chainlinkAggregatorV3Interface(chainlink_rETH_ETH_Oracle).latestRoundData();
    uint256 chainlink_rETH_Price = uint256(reth_price); //in wei
    vm.mockCall(
        reth_oracle,
        abi.encodeWithSelector(IOracle.get.selector),
        abi.encode(true, chainlink_rETH_Price)
    );
    vm.mockCall(
        reth_oracle,
        abi.encodeWithSelector(IOracle.peek.selector),
        abi.encode(true, chainlink_rETH_Price)
    );
    vm.mockCall(
        reth_oracle,
        abi.encodeWithSelector(IOracle.peekSpot.selector),
        abi.encode(chainlink_rETH_Price)
    );

    //deploy bunni oracles
    {
      usdc_weth_bunniOracle = IOracle(new BunniOracle(bunniLens, usdc_weth_bunniToken, usdc_oracle, weth_oracle));

      dai_usdc_bunniOracle = IOracle(new BunniOracle(bunniLens, dai_usdc_bunniToken, dai_oracle, usdc_oracle));

      reth_weth_bunniOracle = IOracle(new BunniOracle(bunniLens, reth_weth_bunniToken, reth_oracle, weth_oracle));
    }

    //set bunni token prices
    (, uint256 usdcAmountBunni1, uint256 wethAmountBunni1) = IBunniLens(bunniLens).pricePerFullShare(IBunniOracle(address(usdc_weth_bunniOracle)).bunni_key());
    bunni_USDC_WETH_Price =
      (usdcAmountBunni1 * chainlink_USDC_Price) / 10 ** ERC20(usdc_weth_pool.token0()).decimals()
      +
      (wethAmountBunni1 * WETH_Price) / 10 ** ERC20(usdc_weth_pool.token1()).decimals();

    (, uint256 daiAmountBunni2, uint256 usdcAmountBunni2) = IBunniLens(bunniLens).pricePerFullShare(IBunniOracle(address(dai_usdc_bunniOracle)).bunni_key());
    bunni_DAI_USDC_Price =
      (daiAmountBunni2 * chainlink_DAI_Price) / 10 ** ERC20(dai_usdc_pool.token0()).decimals()
      +
      (usdcAmountBunni2 * chainlink_USDC_Price) / 10 ** ERC20(dai_usdc_pool.token1()).decimals();

    (, uint256 rethAmountBunni3, uint256 wethAmountBunni3) = IBunniLens(bunniLens).pricePerFullShare(IBunniOracle(address(reth_weth_bunniOracle)).bunni_key());
    bunni_rETH_WETH_Price =
      (rethAmountBunni3 * chainlink_rETH_Price) / 10 ** ERC20(reth_weth_pool.token0()).decimals()
      +
      (wethAmountBunni3 * WETH_Price) / 10 ** ERC20(reth_weth_pool.token1()).decimals();
    
  }

  function test_usdc_weth_bunniOracle() public {
    currentPool = usdc_weth_pool;
    (bool updated_0, uint256 price_0) = usdc_weth_bunniOracle.get();
    //Price should be updated and match
    assertEq(updated_0, true);
    assertEq(price_0, bunni_USDC_WETH_Price);

    (bool updated_1, uint256 price_1) = usdc_weth_bunniOracle.peek();
    //Price should be updated and match
    assertEq(updated_1, true);
    assertEq(price_1, bunni_USDC_WETH_Price);

    uint256 price_2 = usdc_weth_bunniOracle.peekSpot();
    //Price should match
    assertEq(price_2, bunni_USDC_WETH_Price);

    //swap 10 eth for USDC to impact pool
    currentPool.swap(msg.sender, false,  10 * 10**18, UNI_V3_SLIPPAGE, bytes(""));

    (bool updated_3, uint256 price_3) = usdc_weth_bunniOracle.get();
    //Price should be updated and not match
    assertEq(updated_3, true);
    assert(price_3 != price_0);
  }

  function test_dai_usdc_bunniOracle() public {
    currentPool = dai_usdc_pool;
    (bool updated_0, uint256 price_0) = dai_usdc_bunniOracle.get();
    //Price should be updated and match
    assertEq(updated_0, true);
    assertEq(price_0, bunni_DAI_USDC_Price);

    (bool updated_1, uint256 price_1) = dai_usdc_bunniOracle.peek();
    //Price should be updated and match
    assertEq(updated_1, true);
    assertEq(price_1, bunni_DAI_USDC_Price);

    uint256 price_2 = dai_usdc_bunniOracle.peekSpot();
    //Price should match
    assertEq(price_2, bunni_DAI_USDC_Price);

    //swap 100 USDC for Dai to impact pool
    currentPool.swap(msg.sender, false,  100 * 10**6, UNI_V3_SLIPPAGE, bytes(""));

    (bool updated_3, uint256 price_3) = dai_usdc_bunniOracle.get();
    //Price should be updated and not match
    assertEq(updated_3, true);
    assert(price_3 != price_0);
  }

  function test_reth_weth_bunniOracle() public {
    currentPool = reth_weth_pool;
    (bool updated_0, uint256 price_0) = reth_weth_bunniOracle.get();
    //Price should be updated and match
    assertEq(updated_0, true);
    assertEq(price_0, bunni_rETH_WETH_Price);

    (bool updated_1, uint256 price_1) = reth_weth_bunniOracle.peek();
    //Price should be updated and match
    assertEq(updated_1, true);
    assertEq(price_1, bunni_rETH_WETH_Price);

    uint256 price_2 = reth_weth_bunniOracle.peekSpot();
    //Price should match
    assertEq(price_2, bunni_rETH_WETH_Price);

    //swap 10 ETH for rETH to impact pool
    currentPool.swap(msg.sender, false,  10 * 10**18, UNI_V3_SLIPPAGE, bytes(""));

    (bool updated_3, uint256 price_3) = reth_weth_bunniOracle.get();
    //Price should be updated and not match
    assertEq(updated_3, true);
    assert(price_3 != price_0);
  }

  //used when swapping in UNIV3
  function uniswapV3SwapCallback(int256 amount0Delta, int256 amount1Delta, bytes calldata _data) external {
    _data; //get rid of warning
    if(amount0Delta > 0) {
      deal(currentPool.token0(), address(this), uint256(amount0Delta));
      IERC20(currentPool.token0()).transfer(msg.sender, uint256(amount0Delta));
    }
    if(amount1Delta > 0) {
      deal(currentPool.token1(), address(this), uint256(amount1Delta));
      IERC20(currentPool.token1()).transfer(msg.sender, uint256(amount1Delta));
    }
  }

}
