#!/usr/bin/python
'''Coffee Notes - simple crossplatform text jotter
(similar to Notational Velocity for Mac)
Copyright (C) Dmitri dmych Brechalov, 2011
'''
import sys
from PyQt4 import QtCore, QtGui
from main import MainWindow
app = QtGui.QApplication(sys.argv)
win = MainWindow()
win.show()
app.exec_()
