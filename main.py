#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
import os
from utils import *
from notes import Notes

PROG_NAME = 'Coffee Notes'
VERSION = '1.0'
CODE_NAME = 'Espresso'

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
	self.workDir = os.path.expanduser(self.config.readStr('WorkDir', '~/CoffeeNotes'))
	self.notes = Notes(self.workDir)
	self.title = ''
	self.search = ''
	self.changed = None
	self.saving = False
	self.model = QStringListModel(self.notes.index())
	self.noteList.setModel(self.model)
	self.noteList.setSelectionBehavior(QAbstractItemView.SelectRows)
	self.connect(self.noteList, SIGNAL("activated(const QModelIndex&)"), self.selectNote)
	self.connect(self.noteList, SIGNAL("clicked(const QModelIndex&)"), self.selectNote)
	self.connect(self.notes, SIGNAL("indexChanged()"), self.reloadIndex)
	self.connect(self.noteEditor, SIGNAL("textChanged()"), self.textChanged)
	self.connect(self.searchEdit, SIGNAL("textChanged(const QString&)"),
		     self.filterNotes)
	self.autosaveThread = CallbackThread(self.autosave, self.config.readInt('Autosave', 5))
	self.autosaveThread.start(QThread.NormalPriority)

	#### stantard shortcuts
	self.connect(self.searchEdit, SIGNAL("returnPressed ()"), self.openNote)
	shCL = QShortcut(QKeySequence("Ctrl+L"), self)
	shCL.connect(shCL, SIGNAL("activated()"), self.toggleFocus)
	shEsc = QShortcut(QKeySequence("Esc"), self)
	shEsc.connect(shEsc, SIGNAL("activated()"), self.clearSearch)
	shCDel = QShortcut(QKeySequence("Ctrl+Delete"), self)
	shCDel.connect(shCDel, SIGNAL("activated()"), self.deleteNote)
	shCO = QShortcut(QKeySequence("Ctrl+O"), self)
	shCO.connect(shCO, SIGNAL("activated()"), self.changeSplitterOrientation)

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
	self.searchEdit.setFont(QFont(lf, ls))
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
	self.searchEdit.clear()
	self.searchEdit.setFocus()

    def toggleFocus(self):
	if self.searchEdit.hasFocus():
	    self.noteEditor.setFocus()
	else:
	    self.searchEdit.setFocus()

    def reloadIndex(self):
	print 'RELOADING INDEX...'
	idx = self.notes.index()
	try:
	    selected = idx.index(self.title)
	except ValueError:
	    selected = None
	self.model.setStringList(idx)
	if selected is not None:
	    print 'SELECTED:', selected
	    i = self.model.index(selected, 0)
	    self.noteList.setCurrentIndex(i)

    def textChanged(self):
	self.changed = True

    def filterNotes(self, text):
	print 'FIND:', unicode(text)
	self.notes.setFilter(unicode(text))
	self.reloadIndex()

    def autosave(self):
	if self.saving:
	    return
	self.saving = True
	if self.title and self.changed:
	    print 'SAVING...'
	    self._saveText(self.noteEditor.toPlainText())
	    self.changed = False
	self.saving = False

    def openNote(self):
	print 'openNote'
	self.autosave()
	self.title = unicode(self.searchEdit.text())
	print 'TITLE:', self.title
	self.noteEditor.setPlainText(self._readText())
	self.filterNotes('')
	self.noteEditor.setFocus()
	self.changed = False
	#self.notes.indexChanged.emit()

    def selectNote(self):
	sel = self.noteList.selectedIndexes()
	if sel:
	    item = sel[0]
	    title = unicode(self.model.stringList()[item.row()])
	    print 'SELECTED:', item.row(), ':', title
	    self.searchEdit.setText(title)
	    self.openNote()

    def deleteNote(self):
	fname = self.getFileName()
	if fname is not None:
	    print "DELETING", fname
	    os.unlink(fname)
	    self.noteEditor.setPlainText('')
	    self.title = None
	    self.changed = None
	    self.saving = False
	    self.searchEdit.clear()

    def getFileName(self):
	if not self.title:
	    return None
	note = self.notes[self.title]
	if note is None:
	    return os.path.join(self.workDir, self.title + '.txt')
	return note['filename']

    def _readText(self):
	return self.notes.readNote(self.title)

    def _saveText(self, text):
	self.title = self.notes.saveNote(self.title, unicode(text))
	self.searchEdit.setText(self.title)
	self.filterNotes('')
	self.notes.indexChanged.emit()
	
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
