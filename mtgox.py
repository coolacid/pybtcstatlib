#!/usr/bin/env python

import urllib2
import json

def getGox(Ticker):
    req = urllib2.Request("http://data.mtgox.com/api/1/"+ Ticker  +"/ticker")
    try:
	res = urllib2.urlopen(req)
	result = json.load(res)
    except:
	return "GOX-" + Ticker + ": Failed to get data, try again later"

    buy=result["return"]["buy"]["display"]
    sell=result["return"]["sell"]["display"]
    last=result["return"]["last"]["display"]
    high=result["return"]["high"]["display"]
    low=result["return"]["low"]["display"]

    return "GOX-" + Ticker +" -- Buy: " + buy + " | Sell: " + sell + " | Last: " + last + " | High: " + high + " | Low: " + low

def getGoxLast(Ticker):
    req = urllib2.Request("http://data.mtgox.com/api/1/"+ Ticker  +"/ticker")
    try:
	res = urllib2.urlopen(req)
	result = json.load(res)
    except:
	return "GOX-" + Ticker + ": Failed to get data, try again later"

    return result["return"]["last"]["value"]


if __name__ == "__main__":
    print getGoxLast("BTCUSD")
