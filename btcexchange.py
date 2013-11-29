#!/usr/bin/python

import urllib2, json

class BTCEError(Exception):
    def __init__(self, value):
	self.value = value
	print "BTCExchangeError: %s" % value

class BTCExchange():
    def __init__(self):
	self.exchanges = ["GOX", "BFX", "BTCe", "BSTP"]
	self.MtGoxURL = "http://data.mtgox.com/api/1/%s/ticker"
	self.BFXURL = "https://api.bitfinex.com/v1/%s/%s"
	self.BSTPURL = "https://www.bitstamp.net/api/ticker/"
	self.BTCeURL = "https://btc-e.com/api/2/%s/ticker"
	self.Tickers = {
	    "GOX": ["BTCUSD", "BTCEUR", "BTCCAD"],
	    "BFX": ["BTCUSD", "LTCUSD", "LTCBTC"],
	    "BSTP": ["BTCUSD"],
	    "BTCe": ["BTCUSD", "LTCUSD", "BTCEUR", "LTCBTC", "LTCEUR"],
	}

    def Ticker(self, exchange, ticker):
	if len(ticker) == 3:
	    ticker = "BTC%s" % ticker
	if (exchange.upper() == "GOX"):
	    if ticker in self.Tickers["GOX"]:
		url = self.MtGoxURL % ticker.upper()
	    else:
		raise BTCEError("Invalid Ticker")
	elif (exchange.upper() == "BFX"):
	    if ticker in self.Tickers["BFX"]:
		url = self.BFXURL % ("ticker", ticker.lower())
	    else:
		raise BTCEError("Invalid Ticker")
	elif (exchange.upper() == "BTCE"):
	    if ticker in self.Tickers["BTCe"]:
		ticker = ticker[:3] + "_" + ticker[3:]
		url = self.BTCeURL % ticker.lower()
	    else:
		raise BTCEError("Invalid Ticker")
	elif (exchange.upper() == "BSTP"):
	    if ticker in self.Tickers["BSTP"]:
		url = self.BSTPURL 
	    else:
		raise BTCEError("Invalid Ticker")
		url = self.BSTPURL
	else:
	    raise BTCEError("Invalid Exchange: %s" % exchange)
	try:
	    req = urllib2.Request(url)
	    res = urllib2.urlopen(req)
	    result = json.load(res)
	except:
	    raise BTCEError("Failed Receiving Ticker")
	if (exchange.upper() == "GOX"):
	    Value={
		"Last": float(result['return']['buy']['value']),
		"Buy": float(result["return"]["buy"]["value"]),
		"Sell": float(result["return"]["sell"]["value"]),
		"High": float(result["return"]["high"]["value"]),
		"Low": float(result["return"]["low"]["value"])
	    }
	elif (exchange.upper() == "BFX"):
	    Value={
		"Last": float(result["last_price"]),
		"Buy": float(result["bid"]),
		"Sell": float(result["ask"]),
		"High": 0.00,
		"Low": 0.00
	    }
	elif (exchange.upper() == "BTCE"):
	    Value={
		"Last": float(result["ticker"]["last"]),
		"Buy": float(result["ticker"]["buy"]),
		"Sell": float(result["ticker"]["sell"]),
		"High": float(result["ticker"]["high"]),
		"Low": float(result["ticker"]["low"])
	    }
	elif (exchange.upper() == "BSTP"):
	    Value={
		"Last": float(result["last"]),
		"Buy": float(result["bid"]),
		"Sell": float(result["ask"]),
		"High": float(result["high"]),
		"Low": float(result["low"])
	    }
	return Value

    def Orders(self, exchange, ticker, since=0):
	Value=[]
	if len(ticker) == 3:
	    ticker = "BTC%s" % ticker
	if (exchange.upper() == "BFX"):
	    if ticker in self.Tickers["BFX"]:
		if (since > 0):
		    ts = "?timestamp=%d" % int(since)
		url = self.BFXURL % ("trades", ticker.lower()) + ts
	    else:
		raise BTCEError("Invalid Ticker")
	try:
	    req = urllib2.Request(url)
	    res = urllib2.urlopen(req)
	    results = json.load(res)
	except:
	    raise BTCEError("Failed Receiving Ticker")
	if (exchange.upper() == "BFX"):
	    for result in results:
		Value.append({
		    "Timestamp": int(result["timestamp"]),
		    "Price": float(result["price"]),
		    "Amount": float(result["amount"]),
		    "Exchange": result["exchange"],
		})
	    Value = reversed(Value)
	return Value

    def test(self):
	for exchange in self.exchanges:
	    for ticker in self.Tickers[exchange]:
		print exchange, ticker
		try:
		    print self.Ticker(exchange, ticker)
		except BTCEError as e:
		    print "Error: %s" %e.value
		    continue
		except:
		    continue

def main():
    ex = BTCExchange()
#    ex.test()
    value = ex.Orders("BFX", "USD", 1385693109)
    print value
#    print "%.2f" % value['Last']

if __name__ == '__main__':
    main()
