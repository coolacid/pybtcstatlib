#!/usr/bin/python

import sys, time
from btcexchange import *
from PyQt4 import QtCore, QtGui

class SimpleTicker(QtGui.QWidget):
    def __init__(self, exchanges, updatespeed):
        super(SimpleTicker, self).__init__()
	self.exchanges = exchanges
	self.updatespeed = updatespeed
	self.Label = []
	self.Value = []
	self.OValue = []
	self.ex = BTCExchange()
	self.initUI()
	
    def initUI(self):
	i=0
	spacing = 25
        self.center()
        self.setWindowTitle('Simple Ticker')
	font = QtGui.QFont()
	font.setPointSize(20)

	for exchange in self.exchanges:
	    self.Label.append(QtGui.QLabel("%s (%s):" % (exchange[0], exchange[1]), self))
	    self.Value.append(QtGui.QLabel("0", self))
	    self.OValue.append(0)
	    self.Label[i].move (15, 5+(i*spacing))
	    self.Value[i].move (250,5+(i*spacing))
	    self.Label[i].setFont(font)
	    self.Value[i].setFont(font)
	    self.Value[i].setFixedWidth(200)
	    i += 1

        self.resize(400, 22+(i*22))
	self.show()

	self.updateTickers()

    def updateTickers(self):
	i=0
	RED = QtGui.QPalette()
	RED.setColor(QtGui.QPalette.Foreground,QtCore.Qt.red)
	GREEN = QtGui.QPalette()
	GREEN.setColor(QtGui.QPalette.Foreground,QtCore.Qt.darkGreen)

	print "TICK"
	for exchange in self.exchanges:
	    try:
		Value = self.ex.Ticker(exchange[0], exchange[1])
	    except:
		print "GET Failed"
		i += 1
		continue
	    LValue = float(Value["Last"])
	    print "%s-%s: %.2f" % (exchange[0], exchange[1], LValue)
	    if LValue < self.OValue[i]:
		self.Value[i].setPalette(RED)
	    elif LValue > self.OValue[i]:
		self.Value[i].setPalette(GREEN)
	    self.Value[i].setText("%.2f" % LValue)
	    self.OValue[i] = LValue
	    i += 1
	QtCore.QTimer.singleShot(self.updatespeed*1000,self.updateTickers)

    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QtGui.QMessageBox.Yes | 
            QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()  

def main(exchanges, updatespeed):
    app = QtGui.QApplication(sys.argv)
    ex = SimpleTicker(exchanges,updatespeed)
    sys.exit(app.exec_())


if __name__ == '__main__':
    #exchanges = [["GOX", "BTCUSD"],["BFX", "BTCUSD"],["BFX", "LTCUSD"]]
    conf = open("ticker.cfg", "r")
    exchanges = []
    for line in conf:
	exchanges.append (line.strip().split("/"))
    conf.close
    print exchanges
    main(exchanges, 60)
