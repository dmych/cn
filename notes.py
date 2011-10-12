# notes.py: notes database
# this is a part of Coffee Notes project
# Copyright (C) Dmitri `dmych' Brechalov, 2011

import os
import time
from PyQt4.QtCore import *

class Notes(QObject):
    '''General notes DB storing contents in regular text files.
    File names are generated using first line of the text.
    '''
    indexChanged = pyqtSignal()
    def __init__(self, path, sortby='modified'):
	QObject.__init__(self)
	self.path = path
	self.sortby = sortby
	self.filter = None
	self.readDir()
	self.watcher = QFileSystemWatcher([path])
	self.watcher.connect(self.watcher, SIGNAL('directoryChanged (const QString&)'),
		     self._directoryChanged)
	self.watcher.connect(self.watcher, SIGNAL('fileChanged (const QString&)'),
		     self._directoryChanged)

    def _directoryChanged(self, path):
	print 'DIR CHANGED'
	self.readDir()
	self.indexChanged.emit()

    def _sortcmd(self, x, y):
	'''sort by modified date, decremental
	'''
	dx = self._db[x]
	dy = self._db[y]
	if dx[self.sortby] > dy[self.sortby]:
	    return -1
	elif dx[self.sortby] < dy[self.sortby]:
	    return 1
	return 0

    def readDir(self):
	self._db = dict()	# dict indexed by filenames
	for fn in os.listdir(self.path):
	    name, ext = os.path.splitext(fn)
	    if ext.lower() != '.txt':
		continue
	    fullpath = os.path.join(self.path, fn)
	    title = name.decode('utf-8')
	    self._db[title] = {
		'title': title,
		'filename': fullpath,
		'modified': os.path.getmtime(fullpath)
		}

    def index(self):
	result = self.getKeys()
	result.sort(self._sortcmd)
	return result

    def getKeys(self):
	return [ key for key in self._db.keys() if self._matchedFilter(key) ]

    def setFilter(self, filter=None):
	self.filter = filter

    def _matchedFilter(self, key):
	return self.filter is None or key.find(self.filter) > -1

    def __getitem__(self, key):
	'''Return recored for the given title
	or None if not found
	'''
	if self._db.has_key(key):
	    return self._db[key]
	else:
	    return None

if __name__ == '__main__':
    #### testing
    notes = Notes('./Notes')
    for n in notes.index():
	rec = notes[n]
	print n, type(n), time.strftime('%Y-%m-%d %H:%M', time.localtime(rec['modified'])), rec['filename']
