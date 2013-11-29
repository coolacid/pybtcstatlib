#!/usr/bin/python

import urllib2, json, time, datetime
from btcexchange import *

def main():
    last=1
    ex = BTCExchange()
    while 1:
	values = ex.Orders("BFX", "USD", last)
	for value in values:
	    print "%s %.5f %.5f %s" % (datetime.datetime.fromtimestamp(value['Timestamp']).strftime('%H:%M:%S'), value['Price'], value['Amount'], value['Exchange'])
	    last=value['Timestamp']+1
	time.sleep(60)
	print "Tick"

if __name__ == '__main__':
    main()
