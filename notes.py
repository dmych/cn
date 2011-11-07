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

import os
import time
import shelve
from utils import sanitize, log

KEY_PREFIX = 'COFFEE_NOTES_'

class Notes(object):
    '''General notes DB storing contents in regular text files.
    File names are generated using first line of the text.
    '''
    def __init__(self, path, sortby='modifydate'):
	object.__init__(self)
	self.path = path
	log('Open DB...')
	self._db = shelve.open(os.path.join(self.path, '.index.db'))
	self.sortby = sortby
	self.filter = ''
	self.rescanDir()

    def _filepath(self, rec):
	return os.path.join(self.path, rec['filename'])

    def getTitleF(self, fname):
	try:
	    return open(os.path.join(self.path, fname), 'r').readline().strip().decode('utf-8')
	except IOError:
	    return ''

    def getTitle(self, key, ellipsis=60):
	result = self._db[key]['title']
	if len(result) > ellipsis:
	    result = result[:ellipsis] + u'…'
	return result
#	return self.getTitleF(self._db[key])

    def getModifiedFormatted(self, key):
        sec = self._db[key]['modifydate']
        tsec = time.gmtime(sec)
        tnow = time.gmtime(time.time())
        if tsec[:3] == tnow[:3]:
            # today - return time only
            fmt = '%H:%M'
        elif tsec[:2] == tnow[:2]:
            # this month - return Month, Day
            fmt = '%b %d'
        else:
            fmt = '%Y-%m-%d'
        return time.strftime(fmt, time.localtime(sec)) 
    
    def _updateRecord(self, rec):
	if self._db.has_key(rec['key']):
	    dbrec = self._db[rec['key']]
	    dbrec.update(rec)
	else:
	    dbrec = rec
	self._db[rec['key']] = dbrec
	self._db.sync()

    def _newRecord(self):
	md = time.time()
	key = KEY_PREFIX + str(md)
	rec = {
	    'key': key,
	    'title': '',
	    'filename': '',
	    'deleted': 0,
	    'modifydate': md,
	    'createdate': md,
	    'tags': list(),
	    'CHANGED': True,
	    }
	log('*** New note %s' % (key))
	self._updateRecord(rec)
	return rec

    def _addMeta(self, fn):
	fullpath = os.path.join(self.path, fn)
	if not os.path.isfile(fullpath) or fullpath.startswith('.') or not fullpath.endswith('.txt'):
	    return		# skip dirs and other non-file entries
	md = os.path.getmtime(fullpath)
	rec = self._newRecord()
	rec['filename'] = fn
	rec['modifydate'] = md
	rec['createdate'] = md
	rec['title'] = self.getTitleF(fn)
	log('*** %s added as %s' % (fn, rec['key']))
	self._updateRecord(rec)

    def _updateMeta(self, rec):
	fullpath = self._filepath(rec)
	md = os.path.getmtime(fullpath)
	if rec['modifydate'] != md:
	    rec['title'] = self.getTitleF(rec['filename'])
	    rec['modifydate'] = md
	    rec['CHANGED'] = True
	    rec['deleted'] = 0
	    self._updateRecord(rec)
	    log('*** %s (key: %s) changed' % (rec['filename'], rec['key']))

    def rescanDir(self):
	# dict indexed by filenames (without extensions)
	log('Scanning...')
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
		log('*** %s deleted' % fname)
	    
	    if rec.has_key('CHANGED') and rec['CHANGED']:
		self._db[key] = rec
	for fn in flist:	# the rest: new files - add to DB
	    self._addMeta(fn)
	self._db.sync()

    def getKeys(self, deleted=0):
	return [ key for key in self.keys() if self._db[key]['deleted'] == deleted and self._matchedFilter(key) ]

    def _matchedFilter(self, key):
	return not self.filter or self.getContent(key).find(self.filter) > -1

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

    def keys(self):
	return self._db.keys()
    
    def values(self):
	return self._db.values()

    #### Top level interface

    def setFilter(self, filter=''):
	self.filter = filter

    def list(self):
	'''Return list of notes as a tuple: (title_list, key_list)
	where key_list contains keys (filenames) of each note
	'''
	r2 = self.index()
	r1 = [ '%s\n%s' % (self.getTitle(key), self.getModifiedFormatted(key)) for key in r2 ]
	return r1, r2

    def getContent(self, key):
    	try:
    	    return open(self._filepath(self._db[key]), 'r').read().decode('utf-8')
    	except IOError:
    	    return ''

    def getTags(self, key):
	rec = self._db[key]
	if rec.has_key('tags'):
            return ' '.join([ tag.encode('utf-8') for tag in rec['tags']])
	return ''

    def _saveContent(self, rec, text):
    	'''Save the note (rename file and return new filename if necesary)
    	'''
	filename = self._filepath(rec)
    	log('SAVING TO: %s' % filename)
    	open(filename, 'w').write(text.encode('utf-8'))

    def _renameNote(self, rec, first_line):
    	basename = sanitize(first_line)
	newfilename = basename + '.txt'
	i = 1
	while os.path.exists(os.path.join(self.path, newfilename)):
	    newfilename = basename + '-%s' % i + '.txt'
	    i += 1
	npath = os.path.join(self.path, newfilename)
	opath = self._filepath(rec)
	if rec['filename'] and os.path.exists(opath):
	    log('RENAME %s TO %s' % (opath, npath))
	    os.rename(opath, npath)
	log('NEW FILENAME: %s' % newfilename)
	return newfilename

    def saveNote(self, key, text, tags):
	if self._db.has_key(key):
	    rec = self._db[key]
	else:
	    rec = self._newRecord()
	title = text.split('\n')[0].strip().encode('utf-8')
	if title != rec['title']:
	    rec['filename'] = self._renameNote(rec, title)
	    rec['title'] = title
	self._saveContent(rec, text)
	#### update tags
	tags = [ item.strip().decode('utf-8') for item in tags.split(' ') ]
	rec['tags'] = tags
	rec['CHANGED'] = True
	rec['deleted'] = 0
	self._updateMeta(rec)
	return rec['key']

    def deleteNote(self, key):
	if not self._db.has_key(key):
	    return		# no valid key given - just ignore
	rec = self._db[key]
	filename = self._filepath(rec)
	os.unlink(filename)
	rec['deleted'] = 1
	rec['CHANGED'] = True
	self._updateRecord(rec)
	log('*** %s deleted' % key)

    def update(self, rec):
	if rec.has_key('content'):
	    self.!saveContent(rec['content'])
	self._updateRecord(rec)

if __name__ == '__main__':
    #### testing
    VERBOSE = True
    notes = Notes('/home/dbrechalov/Coffee Notes')
    titles, keys = notes.list()
    for i in range(len(titles)):
	print 'TITLE:', titles[i]
	print '  KEY:', keys[i]
	print '   FN:', notes._db[keys[i]]['filename']
