#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
import os
from utils import *
from notes import Notes

PROG_NAME = 'Coffee Notes'
VERSION = '1.1'
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
    def __init__(self, parent=None):
	QMainWindow.__init__(self)
	self._ppath = getProgramPath()
	print self._ppath
	self.config = SimpleConfig('~/.cn.conf')
	uic.loadUi(os.path.join(self._ppath, "main.ui"), self)
	self.connect(self.action_Exit, SIGNAL("triggered()"),
		     self.close)
	self.connect(self.action_About, SIGNAL("triggered()"),
		     self.showAboutBox)
	self.dbname = os.path.expanduser(self.config.readStr('Location', '~/Coffee Notes'))
	self.notes = Notes(self.dbname)
	self.currentKey = None
	self.changed = None
	self.saving = False
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
	#### search box
	self.connect(self.searchBar, SIGNAL("textChanged(const QString&)"),
		     self.filterNotes)
	self.connect(self.searchBar, SIGNAL("returnPressed ()"), self.enterPressed)
	#### autosave
	self.autosaveThread = CallbackThread(self.autosave, self.config.readInt('Autosave', 5))
	self.autosaveThread.start(QThread.NormalPriority)

	#### stantard shortcuts
	shCL = QShortcut(QKeySequence("Ctrl+L"), self)
	shCL.connect(shCL, SIGNAL("activated()"), self.toggleFocus)
	shEsc = QShortcut(QKeySequence("Esc"), self)
	shEsc.connect(shEsc, SIGNAL("activated()"), self.clearSearch)
	shCDel = QShortcut(QKeySequence("Ctrl+Delete"), self)
	shCDel.connect(shCDel, SIGNAL("activated()"), self.deleteNote)
	shCO = QShortcut(QKeySequence("Ctrl+O"), self)
	shCO.connect(shCO, SIGNAL("activated()"), self.changeSplitterOrientation)
	shCS = QShortcut(QKeySequence("Ctrl+S"), self)
	shCS.connect(shCS, SIGNAL('activated()'), self.autosave)

	self.setup()

    def setup(self):
	'''set up fonts etc
	'''
	dft = '%s, %s' % (unicode(self.noteList.font().family()), self.noteList.font().pointSize())
	print 'DEFAULT FONT:', dft
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

    def filterNotes(self, text=''):
	print 'FIND:', unicode(text)
	self.notes.setFilter(unicode(text))
	self.reindex()

    def reindex(self):
	print 'reindex'
	self.notes.rescanDir()
	self.titles, self.keys = self.notes.list()
	self.model.setStringList(self.titles)
	self.indexChanged.emit()
	print '/reindex'

    def selectCurrent(self):
	print 'selectCurrent'
	try:
#	    print '--- 1'
	    cur = self.keys.index(self.currentKey)
#	    print '--- 2'
	    self.noteList.setCurrentIndex(self.model.index(cur))
#	    print '--- 3'
	except ValueError:
	    pass
#	    print '--- !!'
	print '/selectCurrent'

    def autosave(self):
	if self.saving:
	    return
	print 'AUTOSAVE...'
	self.saving = True
	if self.changed:
	    print 'SAVING...'
	    self.saveText()
	    self.changed = False
	self.saving = False

    def openNote(self, key=None):
	print 'openNote', key
	self.autosave()
	self.currentKey = key
	self.noteEditor.setPlainText(self.notes.getContent(self.currentKey))
	self.tagBar.setText(self.notes.getTags(self.currentKey))
	self.changed = False
	self.noteEditor.setFocus()
	self.selectCurrent()
	print '/openNote'

    def enterPressed(self):
	self.noteList.setFocus()

    def selectNote(self):
	print 'selectNote'
	sel = self.noteList.selectedIndexes()
	if sel:
	    item = sel[0]
	    title = self.titles[item.row()]
	    key = self.keys[item.row()]
	    print 'SELECTED:', item.row(), ':', title, key
	    # self.searchBar.setText(title)
	    self.openNote(key)
	print '/selectNote'

    def deleteNote(self):
	pass

    def saveText(self):
	print 'saveText'
	self.notes.saveNote(self.currentKey, unicode(self.noteEditor.toPlainText()), unicode(self.tagBar.text()))
	self.reindex()
	print '/saveText'
	
    def showAboutBox(self):
        QMessageBox.about(self, "About",
                          """<h2>%s</h2>
<h4>Version &laquo;%s&raquo; %s</h4>
<p>&copy; Dmitri Brechalov, 2011</p>
<p>Quick crossplatform notepad inspired by Notational Velocity</p>""" % (PROG_NAME, CODE_NAME, VERSION))


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
