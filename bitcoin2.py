#! /usr/bin/env python

import json, bitcoinrpc, urllib2, shelve

debug = True

class BTCAvgs:
    pass

class bitcoinapi(object):
    def __init__(self, user, password, server="127.0.0.1", port="8332", shelvefile="/tmp/pybtlib"):
	# self.btcd = AuthServiceProxy("http://" + user + ":" + password + "@127.0.0.1:8332")
	self.shelve = shelve.open(shelvefile)
	self.btcd = bitcoinrpc.connect_to_remote(user, password, server, port, False)

    def _decodeCompat(self, bits):
	nbytes = (bits >> 24) & 0xFF
	return (bits & 0xFFFFFF) * (2**(8*(nbytes-3)))

    def _debug(self, message):
	if debug == True:
	    print message

    def get_blockbyhash(self, hash):
	# Need to implement some kind of cache here as this takes the longest to query
	if (self.shelve.has_key(hash.encode("UTF-8"))):
	    return self.shelve[hash.encode("UTF-8")]
	else:
	    block = self.btcd.getblock(hash)
	    self.shelve[hash.encode("UTF-8")] = block
	return block

    def get_blockbynum(self, block):
	# get the hash for the current block
	btchash = self.btcd.getblockhash(block)
	# get the current blocks info
	return self.get_blockbyhash(btchash)

    def get_avgs(self, interval=100):
	# Average time between blocks in seconds
	# get the current block
	currentblockinfo = self.get_blockbynum(self.btcd.getinfo().blocks)
	# self._debug(currentblockinfo.bits)
	parenthash = currentblockinfo.previousblockhash
	time = currentblockinfo.time

	target = self._decodeCompat(int(currentblockinfo.bits, 16))
	avgtarget = target

	lasttime = time
	currentblockinfo = self.get_blockbyhash(parenthash)
	parenthash = currentblockinfo.previousblockhash
	time = currentblockinfo.time
	avgtime = long(lasttime - time)

	target = self._decodeCompat(int(currentblockinfo.bits, 16))
	avgtarget = long((avgtarget + target) / 2.0)

	for i in range(interval):
	    #print parenthash, time, lasttime-time, avgtime #, currentblockinfo.bits, avgtarget
	    lasttime = time
	    currentblockinfo = self.get_blockbyhash(parenthash)
	    parenthash = currentblockinfo.previousblockhash
	    time = currentblockinfo.time
	    avgtime = long(avgtime + (lasttime - time))

	    target = self._decodeCompat(int(currentblockinfo.bits, 16))
	    avgtarget = long((avgtarget + target) / 2.0)

	# get "time" for the last x blocks (using frp, getblock previousblockhash )

	avgtime = avgtime / (interval+1)

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

    def get_avgtime(self, interval=100):
	avgs = self.get_avgs(interval)
	return avgs.time

    def get_currentblock(self):
	# Current block height in the longest chain
	currentblock = self.btcd.getinfo().blocks
	if currentblock is None or currentblock == '':
	    self._debug ("Opps, there was an error, try later")
	    return
	return currentblock

    def get_lastretarget(self):
	blockcount = self.get_currentblock();
	return (blockcount-(blockcount%2016))-1

    def get_hashrate(self):
	# Estimated network hash rate

	avgs = self.get_avgs()
	avgtarget = avgs.target
	avgint = avgs.time

	hashestowin = long(1/(float(avgtarget)/115792089237316195423570985008687907853269984665640564039457584007913129639935))
	hashrate = long(hashestowin / avgint)
	print hashestowin,",",avgint,",",hashrate
	if hashrate is None or hashrate == '':
	    self._debug ("Opps, there was an error, try later")
	    return
	return long(hashrate)

    def get_nextdifficulty(self): # TODO
	# Multiply old difficulty by current avg time
	currentblock = self.get_currentblock()
	lastblock = self.get_lastretarget()+1
	targettime = 600*(currentblock-lastblock+1)

	actualtime = self.get_blockbynum(currentblock).time - self.get_blockbynum(lastblock).time
	oldtarget = self._decodeCompat(int(self.get_blockbynum(lastblock).bits,16))
	if(actualtime<targettime/4):
	    actualtime = targettime/4
	if(actualtime>targettime*4):
	    actualtime = targettime*4
	a = float(oldtarget * actualtime)
	# Divide result by the target
	b = float(a / targettime)
	# Div large number by result
	nextdiff = float(26959535291011309493156476344723991336010898738574164086137773096960 / b)

	if nextdiff is None or nextdiff == '':
	    self._debug ("Opps, there was an error, try later")
	    return
	return nextdiff

    def get_difficulty(self):
	# Current difficulty target as a decimal number
	currentdiff = self.btcd.getinfo().difficulty
	if currentdiff is None or currentdiff == '':
	    self._debug ("Opps, there was an error, try later")
	    return
	return float(currentdiff)

    def get_nextretarget(self):
	# Block height of the next difficulty retarget
	# get the current block
	currentblock = self.get_currentblock()
	mod = currentblock % 2016
	nextretarget = currentblock + (2016 - mod)-1
	if nextretarget is None or nextretarget == '':
	    self._debug ("Opps, there was an error, try later")
	    return
	return nextretarget

    def stat_hash(self):
	# Hash Stats
	currentint = self.get_avgtime()
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
	currentint = self.get_avgtime()

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
    btcapi = bitcoinapi("bitcoinrpc", "43iVCZkbcftfZthwqnRfKJM6nkz9CYGcgKoGkTo2TY7z", shelvefile="./tmpfile")
    # Unit tests
#    print btcapi.get_currentblock()	#-- WORKS
#    print btcapi.get_difficulty()	#-- WORKS
#    print btcapi.get_nextretarget()	#-- WORKS
#    print btcapi.get_avgtime()		#-- Happy
#    print btcapi.get_hashrate()	#-- Happy
#    print btcapi.get_nextdifficulty()	#-- NOT CODED
#    print btcapi.stat_hash()
    print btcapi.stat_diff()
#    print btcapi.stat_estimate (100)
#    print btcapi.stat_estimate (100, 118.4)


