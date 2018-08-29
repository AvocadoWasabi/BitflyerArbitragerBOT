# BitflyerArbitragerBOT
This program is an auto-arbitrage trade for [Bitflyer](https://bitflyer.com/ja-jp/), Bitcoin Exchange Point.

Trade target is price gaps between Bitcoin spot trading and futures.

**This program was recently published, please report bugs**

# What's Arbitrage Trade?
Trade method using price gaps of two or + markets with sililar financial instrument.

## Example

Market A 100yen/BTC, Market B 110yen/BTC

If we sell 1BTC at Market B and BUY 1BTC at Market A, we can earn 110-100=10yen.

This profit is ensured with reason that these two market treat same financial instrument and price will be same after a while.

Spot trading and Futures will be the same price at SQ time, so this fact enables arbitrage trade.

This method said to be low risk and low return.

# Screenshot
screenshot shows...

1. logging time
2. Trade Pair `[spot_trading][futures]:size`
3. besk_ask, besk bid, each size
4. showing expectable profit(normal is minus value = no arbitrage oppotunity)

![screen](https://github.com/AvocadoWasabi/BitflyerArbitragerBOT/blob/ReadmeImages/images/screen.PNG)


# License
See file `LICENSE`. 2 licenses included by part.

# Disclaimer
USE THIS PROGRAM AT YOUR OWN RISK.

# Envioronment and requirements
## Language and Version
Python 3.6.4

## PC time
Adjust PC time accurately for avoiding time gap with Bitflyer server time.

## Libraries
install `requests` and `six`

```
pip install requests
pip install six
```

## API KEY and SECRET
Get Bitflyer API KEY and SECRET for auto-trading.

Set API Authorization below.

**KEEP API KEYS AND SECRET IN SAFE PLACE**

![API Authorization](https://github.com/AvocadoWasabi/BitflyerArbitragerBOT/blob/ReadmeImages/images/authorization_limitation.png)

## Account condition
Prepare money for trade.

Set levarage at **x1** for avoiding loss-cut.

Money balance is X for spot trading, 1.8X for futures.

Get extra BTC for commission.

### Example
max position 20,000 yen for each side.

spot trading : 20,000 yen

futures : 38,000 yen(18,000 for deposit)

0.003 BTC for commission

# Installation

1. Install Python 3.6.4
2. Fork or git clone this repository.
3. Get API KEY and SECRET. Prepare money on your account.
4. Rename `config_default.json` to `config.json`
5. Set items of `config.json`
6. Run `main.py`

# Settings
List of `config.json` setting

|items|descriptions|
|:----|:-----------|
|demo_mode|`true`:virtual trade, `false`:real trade|
|demo_trade_interval|trade interval of demo mode. not real trade|
|message_language|`EN`:English `JP`:Japanese|
|api_key|Set Bitflyer API KEY|
|api_secret|Set Bitflyer API SECRET|
|swap_point_rate|Futures Swap point rate|
|position_value|Trade amount at one trade(BTC). For *each* assets(ex.spot trading, futures)|
|max_position_value|Max trade amount(BTC) For *each* assets(ex.spot trading, futures)|
|expect_profit_threshold|Do arbitrage trade when expect profit(yen) is more than this value|
|close_pair_before_sq|When `spot trading price > futures price`, close position|
|closing_margin_time|If above condition is kept for this value[sec], close position.(close_pair_before_sq shoulf be true)|
|maturity_time|Maturity time of futures|
|maturity_time_margin|Buffer time of maturity time[sec] for avoiding problems of time gap between PC and server|
|itayose_time|spot trading itayose time|
|sq_time|SQ settlement time|
|std_stream_logging_interval|Showing interval of regular log|
|arbitrage_loop_cooling_time|Arbitrage trade interval during continuous trade oppotunity|
|websocket_retry_after|Retry Websocket connection after this value[sec]|
|arbitrage_debug_mode|Get virtual arbitrage oppotunity data.**Set DEMOMODE to use it, or real trade with fake data**|
|maturity_debug_mode|Make the program run virtual maturity, iyayose and reboot time|
|debug_maturity_start|For debug, virtual maturity time|
|debug_itayose_start|For debug, virtual itayose time|
|debug_reboot_start|For debug, virtual reboot time|

# Architecture
## modules
Program modules are made along multiprocessing.

![Architecture](https://github.com/AvocadoWasabi/BitflyerArbitragerBOT/blob/ReadmeImages/images/architecture.png)

## Arbitrage Oppotunity Detail
`(Futures best bid) - (Spot trading best ask) - 2 x (commission) - swap point = expect profit`

If `expect profit > expect_profit_threshold`, the program regards it as an arbitrade oppotunity.

This oppotunity often occures when BTC price goes down rapidly, or when maturity time comes close.

## Boot and Reboot
`config.json` is read when boot and reboot.

Dynamic setting change isn't supported.

## Log output
`yyyymmdd.log` for level-info log.

`yyyymmdd_high_level` for level-warning log for tracing trade log.

## product_code
Product_code is the identifier of each Bitflyer board.

ex. BTC_JPY : spot_trading, BTCJPY24AUG2018: Futures with maturity date(August 24)

# Inspirations
[r2 arbitrager](https://github.com/bitrinjani/r2), Arbitrager BETWEEN BTC Exchange points.
