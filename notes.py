# notes.py: notes database
# this is a part of Coffee Notes project
# Copyright (C) Dmitri `dmych' Brechalov, 2011

import os
import time
import shelve
from utils import sanitize

KEY_PREFFIX = 'COFFEE_NOTES_'

VERBOSE = False

def dbg(msg):
    if VERBOSE:
	print msg

class Notes(object):
    '''General notes DB storing contents in regular text files.
    File names are generated using first line of the text.
    '''
    def __init__(self, path, sortby='modifydate'):
	object.__init__(self)
	self.path = path
	dbg('Open DB...')
	self._db = shelve.open(os.path.join(self.path, '.index.db'))
	self.sortby = sortby
	self.filter = ''
	self.rescanDir()

    def _filepath(self, key):
	return os.path.join(self.path, self._db[key]['filename'])

    def _getTitle(self, key):
	try:
	    return open(self._filepath(key), 'r').readline().strip().decode('utf-8')
	except IOError:
	    return ''

    def _updateRecord(self, rec):
	if self._db.has_key(rec['key']):
	    dbrec = self._db[rec['key']]
	    dbrec.update(rec)
	else:
	    dbrec = rec
	self._db[rec['key']] = dbrec

    def _addMeta(self, fn):
	fullpath = os.path.join(self.path, fn)
	if not os.path.isfile(fullpath) or fullpath.startswith('.') or not fullpath.endswith('.txt'):
	    return		# skip dirs and other non-file entries
	md = os.path.getmtime(fullpath)
	key = KEY_PREFFIX + str(md)
	rec = {
	    'key': key,
	    'filename': fn,
	    'deleted': 0,
	    'modifydate': md,
	    'createdate': md,
	    'tags': list(),
	    'CHANGED': True,
	    }
	dbg('*** %s added as %s' % (fn, key))
	self._updateRecord(rec)

    def _updateMeta(self, rec):
	fullpath = self._filepath(rec['key'])
	md = os.path.getmtime(fullpath)
	if rec['modifydate'] != md:
	    rec['modifydate'] = md
	    rec['CHANGED'] = True
	    rec['deleted'] = 0
	    self._updateRecord(rec)
	    dbg('*** %s (key: %s) changed' % (rec['filename'], rec['key']))

    def rescanDir(self):
	# dict indexed by filenames (without extensions)
	dbg('Scanning...')
	flist = os.listdir(self.path)
	for key in self.getKeys():
	    rec = self._db[key]
	    fname = rec['filename']
	    try:	 # check: does the file exists and update info
		flist.remove(fname)
		self._updateMeta(rec)
	    except ValueError:	# no such file - deleted
		rec['deleted'] = 1
		rec['CHANGED'] = True
		dbg('*** %s deleted' % fname)
	    
	    if rec.has_key('CHANGED') and rec['CHANGED']:
		self._db[key] = rec
	for fn in flist:	# the rest: new files - add to DB
	    self._addMeta(fn)
	self._db.sync()

    def getKeys(self, deleted=0):
	return [ key for key in self._db.keys() if self._db[key]['deleted'] == deleted and self._matchedFilter(key) ]

    def _matchedFilter(self, key):
	return self.filter is None or self.getContent(key).find(self.filter) > -1

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

    def index(self, deleted=0):
	result = self.getKeys(deleted)
	result.sort(self._sortcmd)
	return result

    #### Top level interface

    def setFilter(self, filter=''):
	self.filter = filter

    def list(self):
	'''Return list of notes as a tuple: (title_list, key_list)
	where key_list contains keys (filenames) of each note
	'''
	r2 = self.index()
	r1 = [ self._getTitle(key) for key in r2 ]
	return r1, r2

    def getContent(self, key):
    	try:
    	    return open(self._filepath(key), 'r').read().decode('utf-8')
    	except IOError:
    	    return ''

    def getTags(self, key):
	rec = self._db[key]
	if rec.has_key('tags'):
            return ' '.join([ tag.encode('utf-8') for tag in rec['tags']])
	return ''

    def _saveContent(self, filename, text):
    	'''Save the note (rename file and return new filename if necesary)
    	'''
    	newfilename = sanitize(text.split('\n')[0].strip().encode('utf-8')) + '.txt'
	path_fn = os.path.join(self.path, filename)
	path_nf = os.path.join(self.path, newfilename)
    	if filename != newfilename and os.path.exists(path_fn):
    	    os.rename(path_fn, path_nf)
    	    print 'RENAME:', path_fn
    	    print 'TO:    ', path_nf
    	    filename = newfilename
	    path_fn = path_nf
    	print 'SAVING TO:', filename
    	open(path_fn, 'w').write(text.encode('utf-8'))
    	return filename

    def saveNote(self, key, text, tags):
	rec = self._db[key]
	if not rec.has_key('filename'):
	    #### no filename given - use the first line of the text
	    fn = sanitize(text.split('\n')[0].strip())
	    if not fn:		# or key if text is empty
		fn = key
	    rec['filename'] = fn
	rec['filename'] = self._saveContent(rec['filename'], text)
	#### update tags
	tags = [ item.strip().decode('utf-8') for item in tags.split(' ') ]
	rec['tags'] = tags
	rec['CHANGED'] = True
	rec['deleted'] = 0
	self._updateRecord(rec)

    ########
	
    def __getitem__(self, key):
	'''Return a note by the given key
	'''
	print('**** TODO ****')

    def __setitem__(self, key, note):
	'''Replaces a note with the given key with the given note
	'''
	print('**** TODO ****')

    # def __getitem__(self, key):
    # 	'''Return record for the given title
    # 	or None if not found
    # 	'''
    # 	if self._db.has_key(key):
    # 	    return self._db[key]
    # 	else:
    # 	    return None

    # def readNote(self, key):
    # 	note = self.__getitem__(key)
    # 	if note is None:
    # 	    return ''
    # 	try:
    # 	    return open(note['filename'], 'r').read().decode('utf-8')
    # 	except IOError:
    # 	    return ''

    # def saveNote(self, key, text):
    # 	'''Save the note (rename file and change title if necesary)
    # 	Return new title
    # 	'''
    # 	note = self.__getitem__(key)
    # 	title = text.split('\n')[0].strip()
    # 	print '^' * 20
    # 	print 'OLD TITLE:', key
    # 	print 'NEW TITLE:', title
    # 	if note is None:
    # 	    note = {
    # 		'title': title,
    # 		'filename': os.path.join(self.path, self._sanitize(title)) + '.txt'
    # 		}
    # 	    print 'NEW NOTE!'
    # 	elif key != title:
    # 	    newname = os.path.join(self.path, self._sanitize(title)) + '.txt'
    # 	    os.rename(note['filename'], newname)
    # 	    print 'RENAME:', note['filename']
    # 	    print 'TO:    ', newname
    # 	    note['filename'] = newname
    # 	print 'SAVING TO:', note['filename']
    # 	open(note['filename'], 'w').write(text.encode('utf-8'))
    # 	print '^' * 20
    # 	return title

if __name__ == '__main__':
    #### testing
    VERBOSE = True
    notes = Notes('/home/dbrechalov/Coffee Notes')
    titles, keys = notes.list()
    for i in range(len(titles)):
	print 'TITLE:', titles[i]
	print '  KEY:', keys[i]
	print '   FN:', notes._db[keys[i]]['filename']
