#!/usr/bin/python
# This file is part of Coffee Notes project
# 
# Coffee Notes is a crossplatform note-taking application
# inspired by Notational Velocity.
# <https://github.com/dmych/cn>
# 
# Copyright (c) Dmitri Brechalov, 2011
# 
# Coffee Notes is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Coffee Notes is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

import sys
from PyQt4 import QtCore, QtGui
from main import MainWindow
app = QtGui.QApplication(sys.argv)
win = MainWindow()
win.show()
app.exec_()
