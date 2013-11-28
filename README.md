Simple Python Libs to gather information from web appis or bitcoind and generate different stats

Use the source luke!

Running the file should produce simple results.

bitcoin.py - Pulls data from API sources
- I never intended to relase the code, so I didn't note where some came from. 
- In my google search, I should mention the following:
- https://github.com/nanotube/supybot-bitcoin-marketmonitor/blob/master/BitcoinData/plugin.py#L58

bitcoin2.py - Pulls data from Bitcoind
- bitcoin2.py makes use of: https://github.com/laanwj/bitcoin-python
- Most of the calculations comes from https://github.com/lirazsiri/blockexplorer/blob/master/htdocs/includes/app_stats.inc

btcexchange.py - Query data from different exchanges
- Call the ticker with (exchange, market)
- It does some internal fixes of markets based on the exchange

ticker.py - Simple PyQt Ticker
- Needs work, first Qt Python script
- See ticker.cfg for example config

Please Support: 
BTC: 1DawBdois5GkteqbHrUkA5syYX4Xs2NFd4
LTC: LfgTr3TUFm8jMFXmwVk26vQWrQK8rNMwJN

If you use any Lib, please, let me know in an "issue" ;)