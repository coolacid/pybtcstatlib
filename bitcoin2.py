#! /usr/bin/env python

from urllib2 import urlopen
import json, bitcoinrpc

debug = True

class BTCAvgs:
    pass

class bitcoinapi(object):
    def __init__(self, user, password, server="127.0.0.1", port="8332"):
	# self.btcd = AuthServiceProxy("http://" + user + ":" + password + "@127.0.0.1:8332")
	self.btcd = bitcoinrpc.connect_to_local()

    def _decodeCompat(self, bits):
	nbytes = (bits >> 24) & 0xFF
	return (bits & 0xFFFFFF) * (2**(8*(nbytes-3)))

    def _debug(self, message):
	if debug == True:
	    print message

    def _grabapi(self, apipaths):
	# This will attempt to grab the information using blockchain first, then blockexplorer.
        sources = ['http://blockchain.info', 'http://blockexplorer.com']
        urls = [''.join(t) for t in zip(sources, apipaths)]
	# print urls
        for url in urls:
            try:
		self._debug ("Getting: " + url)
		user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
		headers = { 'User-Agent' : user_agent }
		bitOpen = urllib2.Request(url, "", headers)
		data = urllib2.urlopen(bitOpen).read()
                #data = urlopen(url, timeout=5).read()
		if data == '':
		    self._debug ("Got a blank response")
		    continue
		self._debug ("Got: " + data)
                return data
            except Exception, e: 
		self._debug (e)
                continue
        return None

    def get_avgs(self, interval=10):
	# Average time between blocks in seconds
	# get the current block
	currentblock = self.btcd.getinfo().blocks
	# get the hash for the current block
	btchash = self.btcd.getblockhash(currentblock)
	# get the current blocks info
	currentblockinfo = self.btcd.getblock(btchash)
	# self._debug(currentblockinfo.bits)
	parenthash = currentblockinfo.previousblockhash
	time = currentblockinfo.time
	avgtime = 0

	target = self._decodeCompat(int(currentblockinfo.bits, 16))
	avgtarget = target

	for i in range(interval):
	    print parenthash, time, avgtime, currentblockinfo.bits, avgtarget
	    lasttime = time
	    currentblockinfo = self.btcd.getblock(parenthash)
	    parenthash = currentblockinfo.previousblockhash
	    time = currentblockinfo.time
	    avgtime = long((avgtime + (lasttime - time)) / 2)

	    target = self._decodeCompat(int(currentblockinfo.bits, 16))
	    avgtarget = long((avgtarget + target) / 2.0)

	# get "time" for the last x blocks (using frp, getblock previousblockhash )

	if avgtarget is None or avgtarget == '':
	    self._debug ("Opps, there was an error, try later")
	    return

	if avgtime is None or avgtime == '':
	    self._debug ("Opps, there was an error, try later")
	    return

	avgs = BTCAvgs()
	avgs.time = avgtime
	avgs.target = avgtarget
	return avgs

    def get_interval(self, interval=100):
	avgs = self.get_avgs(interval)
	return avgs.time

    def get_currentblock(self):
	# Current block height in the longest chain
	#currentblock = self._grabapi(['/q/getblockcount']*2)
	currentblock = self.btcd.getinfo().blocks
	if currentblock is None or currentblock == '':
	    self._debug ("Opps, there was an error, try later")
	    return
	return float(currentblock)

    def get_hashrate(self):
	# Estimated network hash rate in gigahash
	#hashrate = self._grabapi(['/q/hashrate']*2)

	avgs = self.get_avgs()
	avgtarget = avgs.target
	avgint = avgs.time

	hashestowin = long(1/(float(avgtarget)/115792089237316195423570985008687907853269984665640564039457584007913129639935))
	print hashestowin
	hashrate = long(hashestowin / avgint)
	if hashrate is None or hashrate == '':
	    self._debug ("Opps, there was an error, try later")
	    return
	return long(hashrate)

    def get_nextdifficulty(self): # TODO
	# Get the next difficulty (Only available from blockexplorer)
	nextdiff = self._grabapi(['/q/estimate']*2)
	if nextdiff is None or nextdiff == '':
	    self._debug ("Opps, there was an error, try later")
	    return
	return float(nextdiff)

    def get_difficulty(self):
	# Current difficulty target as a decimal number
	#currentdiff = self._grabapi(['/q/getdifficulty']*2)
	currentdiff = self.btcd.getinfo().difficulty
	if currentdiff is None or currentdiff == '':
	    self._debug ("Opps, there was an error, try later")
	    return
	return float(currentdiff)

    def get_nextretarget(self): # TODO -- TEST
	# Block height of the next difficulty retarget
	#nextretarget = self._grabapi(['/q/nextretarget']*2)
	# get the current block
	currentblock = self.btcd.getinfo().blocks
	mod = currentblock % 2016
	nextretarget = currentblock + (2016 - mod)-1
	if nextretarget is None or nextretarget == '':
	    self._debug ("Opps, there was an error, try later")
	    return
	return float(nextretarget)

    def stat_hash(self):
	# Hash Stats
	currentint = self.get_interval()
	currentblock = self.get_currentblock()
	hashrate = self.get_hashrate()

	if currentint is None or currentblock is None or hashrate is None:
	    return "There was an error, please try again later"

	m, s = divmod(currentint, 60)
	abouttime = "%02d Minutes %02d Seconds" % (m, s)
	data = "Estimated interval between blocks: %s | Current Block: %d | Global Hashrate: %.2f GH/s " % (abouttime, currentblock, hashrate)
	return data

    def stat_diff(self):
	# Difficulty Stats
	nextretarget = self.get_nextretarget()
	currentblock = self.get_currentblock()
	nextdiff = self.get_nextdifficulty()
	currentdiff = self.get_difficulty()
	currentint = self.get_interval()

	if nextretarget is None or currentblock is None or nextdiff is None or currentdiff is None or currentint is None:
	    return "There was an error, please try again later"

	nextin = nextretarget - currentblock
	diffchange = (nextdiff - currentdiff) / currentdiff * 100
	timetochange = nextin * currentint
	m, s = divmod(timetochange, 60)
	h, m = divmod(m, 60)
	d, h = divmod(h, 24)
	abouttime = "%d Days %d Hours %02d Minutes %02d Seconds" % (d, h, m, s)
	data = "Cur Dif: %.2f | Est Next: %.2f (%.2f%%) | Next Diff change in: %d Blocks (~%s)" % (currentdiff, nextdiff, diffchange, nextin, abouttime)
	return data

    def stat_estimate(self, hashrate, quote=0):
	currentdiff = self.get_difficulty()

	if currentdiff is None:
	    return "There was an error, please try again later"

	estimate = 24 / (currentdiff * 2**32 / ( hashrate * 10**6) / 60 / 60) * 25
	if quote == 0:
	    data = "At %d MH/s, you should earn on avg ~%f BTC/day or %f BTC/hr." % (hashrate, estimate, (estimate/24))
	else:
	    data = "At %d MH/s, you should earn on avg ~%f BTC/day ($%f USD) or %f BTC/hr." % (hashrate, estimate, (estimate*quote), (estimate/24))
	return data



if __name__ == "__main__":
    btcapi = bitcoinapi("bitcoinrpc", "43iVCZkbcftfZthwqnRfKJM6nkz9CYGcgKoGkTo2TY7z")
    # Unit tests
#    print btcapi.get_currentblock()	#-- WORKS
#    print btcapi.get_difficulty()	#-- WORKS
#    print btcapi.get_nextretarget()	#-- WORKS
#    print btcapi.get_interval(20)	#-- Close
    print btcapi.get_hashrate()		#-- Close
#    print btcapi.get_nextdifficulty()	#-- NOT CODED
#    print btcapi.stat_hash()
#    print btcapi.stat_diff()
#    print btcapi.stat_estimate (100)
#    print btcapi.stat_estimate (100, 118.4)


