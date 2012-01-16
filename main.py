#!/usr/bin/python
# -*- coding: utf-8 -*-
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
# along with Coffee Notes.  If not, see <http://www.gnu.org/licenses/>.

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
import os
from utils import *
from notes import Notes

PROG_NAME = 'Coffee Notes'
VERSION = '12.00a'
CODE_NAME = 'Americano'

class CallbackThread(QThread):
    '''Execute callback once at 5 secs
    '''
    def __init__(self, callback, sec=5, parent=None):
	QThread.__init__(self, parent)
	self.callback = callback
	self.sec = sec
    def run(self):
	while True:
	    self.callback()
	    self.sleep(self.sec)

class MainWindow(QMainWindow):
    indexChanged = pyqtSignal()
    saveRequested = pyqtSignal()
    def __init__(self, parent=None):
	QMainWindow.__init__(self)
	self._ppath = getProgramPath()
	log('PATH: %s' % self._ppath, True)
	self.config = SimpleConfig('~/.cn.conf')
	uic.loadUi(os.path.join(self._ppath, "main.ui"), self)
	self.connect(self.action_Exit, SIGNAL("triggered()"),
		     self.close)
	self.connect(self.action_About, SIGNAL("triggered()"),
		     self.showAboutBox)
	self.dbname = os.path.expanduser(self.config.readStr('WorkDir', '~/Coffee Notes'))
	self.notes = Notes(self.dbname)
	self.saving = False
	self.currentKey = None
	self.changed = False
	self.newNote()
	#### notes list behaviour
	self.model = QStringListModel() # !!
	self.noteList.setModel(self.model)
	self.noteList.setSelectionBehavior(QAbstractItemView.SelectRows)
	self.connect(self.noteList, SIGNAL("activated(const QModelIndex&)"), self.selectNote)
	self.connect(self.noteList, SIGNAL("clicked(const QModelIndex&)"), self.selectNote)
	self.filterNotes()
	self.connect(self, SIGNAL("indexChanged()"), self.selectCurrent)
	#### text editor & tag bar
	self.connect(self.noteEditor, SIGNAL("textChanged()"), self.textChanged)
	self.connect(self.tagBar, SIGNAL("textChanged(const QString&)"), self.textChanged)
	self.connect(self.deleteButton, SIGNAL("clicked()"), self.deleteNote)
	self.noteEditor.setAcceptRichText(False)
	self.noteEditor.setTabChangesFocus(True)
	#### search box
	self.connect(self.searchBar, SIGNAL("textChanged(const QString&)"),
		     self.filterNotes)
	self.connect(self.searchBar, SIGNAL("returnPressed ()"), self.enterPressed)
	self.connect(self.addButton, SIGNAL("clicked()"), self.newNote)
	self.connect(self.syncButton, SIGNAL("clicked()"), self.startSync)
	#### autosave
	self.connect(self, SIGNAL('saveRequested()'), self.saveText)
	sec = self.config.readInt('Autosave', 5)
	if sec <= 0: sec = 5
	self.autosaveThread = CallbackThread(self.autosave, sec)
	self.autosaveThread.start(QThread.IdlePriority)

	#### stantard shortcuts
	shCL = QShortcut(QKeySequence("Ctrl+L"), self)
	shCL.connect(shCL, SIGNAL("activated()"), self.toggleFocus)
	shEsc = QShortcut(QKeySequence("Esc"), self)
	shEsc.connect(shEsc, SIGNAL("activated()"), self.clearSearch)
	shCN = QShortcut(QKeySequence("Ctrl+N"), self)
	shCN.connect(shCN, SIGNAL("activated()"), self.newNote)
	shCD = QShortcut(QKeySequence("Ctrl+D"), self)
	shCD.connect(shCD, SIGNAL("activated()"), self.deleteNote)
	shCO = QShortcut(QKeySequence("Ctrl+O"), self)
	shCO.connect(shCO, SIGNAL("activated()"), self.changeSplitterOrientation)
	shCS = QShortcut(QKeySequence("Ctrl+S"), self)
	shCS.connect(shCS, SIGNAL('activated()'), self.startSync)

	self.setup()

    def setup(self):
	'''set up fonts etc
	'''
	dft = '%s, %s' % (unicode(self.noteList.font().family()), self.noteList.font().pointSize())
	log('DEFAULT FONT: %s' % dft)
	lf = self.config.readStr('ListFont', dft)
	try:
	    (lf, ls) = lf.split(',', 1)
	    ls = int(ls.strip())
	except:
	    ls = self.noteList.font().pointSize()
	ef = self.config.readStr('EditFont', dft)
	try:
	    (ef, es) = ef.split(',', 1)
	    es = int(es.strip())
	except:
	    es = self.noteList.font().pointSize()
	self.noteList.setFont(QFont(lf, ls))
	self.searchBar.setFont(QFont(lf, ls))
	self.noteEditor.setCurrentFont(QFont(ef, es))
	self.restoreSettings()

    def quit(self):
#	self.autosave()
	qApp.quit()

    def closeEvent(self, event):
	self.autosave()
	self.saveSettings()
	event.accept()

    def clearSearch(self):
	self.searchBar.clear()
	self.searchBar.setFocus()

    def toggleFocus(self):
	if self.searchBar.hasFocus():
	    self.noteEditor.setFocus()
	else:
	    self.searchBar.setFocus()

    def textChanged(self, text=None):
	self.changed = True
	self.statusBar().clearMessage()

    def filterNotes(self, text=''):
	log('FIND: %s' % unicode(text).encode('utf-8'))
	self.notes.setFilter(unicode(text))
	if text:
	    log('%s' % type(text))
	    self.noteList.keyboardSearch(text)
	self.reindex()

    def reindex(self):
	log('reindex')
	self.statusBar().showMessage('Scanning directory...')
#	self.notes.rescanDir()
	self.titles, self.keys = self.notes.list()
	self.model.setStringList(self.titles)
	self.indexChanged.emit()
	self.statusBar().showMessage('%s notes' % (len(self.titles)))
	log('/reindex')

    def selectCurrent(self):
	log('selectCurrent')
	try:
	    cur = self.keys.index(self.currentKey)
	    self.noteList.setCurrentIndex(self.model.index(cur))
	except ValueError:
	    pass
	log('/selectCurrent')

    def autosave(self):
	self.saveRequested.emit()

    def newNote(self):
	self.autosave()
	self.noteEditor.clear()
	self.tagBar.clear()
	self.currentKey = None
	self.changed = False
	self.noteEditor.setFocus()
	self.statusBar().clearMessage()

    def openNote(self, key=None):
	log('openNote(%s)' % key)
	self.autosave()
	self.currentKey = key
	self.noteEditor.setPlainText(self.notes.getContent(self.currentKey))
	self.tagBar.setText(self.notes.getTags(self.currentKey))
	self.changed = False
	self.noteEditor.setFocus()
	self.selectCurrent()
	self.statusBar().clearMessage()
	log('/openNote')

    def enterPressed(self):
	self.noteList.setFocus()

    def selectNote(self):
	log('selectNote')
	sel = self.noteList.selectedIndexes()
	if sel:
	    item = sel[0]
	    title = self.titles[item.row()]
	    key = self.keys[item.row()]
	    log('SELECTED: %s: %s [%s]' % (item.row(), title.encode('utf-8'), key))
	    # self.searchBar.setText(title)
	    self.openNote(key)
	log('/selectNote')

    def deleteNote(self):
	if self.currentKey is None:
	    return
	ans = QMessageBox.question(self, "Delete", "Delete \"%s\"?" % self.notes.getTitle(self.currentKey), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
	if ans != QMessageBox.Yes:
	    return
	self.notes.deleteNote(self.currentKey)
	self.noteEditor.clear()
#	self.tagBar.clear()
	self.currentKey = None
	self.changed = False
	self.reindex()

    def saveText(self):
	if self.saving:
	    return
	self.saving = True
	if self.changed:
	    log('SAVING...')
	    self.statusBar().showMessage('Saving...')
	    self.currentKey = self.notes.saveNote(self.currentKey, unicode(self.noteEditor.toPlainText()), unicode(self.tagBar.text()))
	    self.reindex()
	    self.changed = False
	    self.statusBar().showMessage('Saved')
	self.saving = False
	
    def showAboutBox(self):
        QMessageBox.about(self, "About",
                          """<h2>%s</h2>
<h4>Version &laquo;%s&raquo; %s</h4>
<p>&copy; Dmitri Brechalov, 2011-2012</p>
<p>Crossplatform note-taking application inspired by Notational Velocity</p>
<p><small>This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.<br/>
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.<br/>
You should have received a copy of the GNU General Public License
along with this program.  If not, see <a href="http://www.gnu.org/licenses/">http://www.gnu.org/licenses/</a>.
""" % (PROG_NAME, CODE_NAME, VERSION))


    def changeSplitterOrientation(self):
	orientation = self.splitter.orientation()
	if orientation == Qt.Horizontal:
	    orientation = Qt.Vertical
	else:
	    orientation = Qt.Horizontal
	self.splitter.setOrientation(orientation)

    def saveSettings(self):
	settings = QSettings("dmych", PROG_NAME)
	settings.setValue("geometry", self.saveGeometry())
	settings.setValue("state", self.saveState())
	settings.setValue("splitter", self.splitter.saveState())

    def restoreSettings(self):
	settings = QSettings("dmych", PROG_NAME)
	self.restoreGeometry(settings.value("geometry").toByteArray())
	self.restoreState(settings.value("state").toByteArray())
	self.splitter.restoreState(settings.value("splitter").toByteArray())

    def startSync(self):
	self.statusBar().showMessage('Sync started...')
