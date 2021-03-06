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

LOGNAME = '/tmp/cn.log'
def log(msg, restart=False):
    if restart:
	f = open(LOGNAME, 'w')
    else:
	f = open(LOGNAME, 'a')
    f.write('%s\n' % msg)
    f.close()

def getProgramPath():
    import sys
    import os.path
    pname = sys.argv[0]
    if os.path.islink(pname):
        pname = os.readlink(pname)
    return os.path.abspath(os.path.dirname(pname))

def openConfig(fname, mode):
    '''Return config file object'''
    import os.path
    return open(os.path.expanduser(fname), mode)

class SimpleConfig:
    def __init__(self, fileName):
        self.data = {}
        self.fileName = fileName
        self.__readData()

    def __readData(self):
        self.data = {}
        try:
            f = openConfig(self.fileName, 'r')
        except:
	    log('CANNOT FIND %s' % self.fileName)
            return
        for line in f.readlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue     # just empty line or comment
            try:
                (key, value) = line.split('=', 1)
                self.data[key] = value
            except:
                pass
        f.close()
	log('CONFIG')
	log(repr(self.data))

    def save(self):
        f = openConfig(self.fileName, 'w')
        for (k, v) in self.data.items():
            f.write('%s=%s\n' % (k, v))
        f.close()

    def close(self):
        self.save()

    def clear(self):
        self.data.clear()

    def readStr(self, key, default=None):
        try:
            value = self.data[key]
        except:
            value = default
        return value

    def readInt(self, key, default=None):
        try:
            return int(self.readStr(key))
        except:
            return default

    def readBool(self, key, default=False):
        try:
            return bool(self.readInt(key))
        except:
            return default

    def keys(self, start=None):
        if start:
            result = [ item for item in self.data.keys() \
                       if item.startswith(start) ]
        else:
            result = self.keys()
        return result

    def values(self, start=None):
        keys = self.keys(start)
        result = [ self.data[k] for k in keys ]
        return result

    def writeStr(self, key, value):
        self.data[key] = str(value)
        
    writeInt = writeStr
        
    def writeBool(self, key, value):
        self.writeStr(key, int(value))

def strip_hashes(txt):
    '''Strip all hashes and spaces at the begining and the end of line
    '''
    while txt and txt[0] in '# \t':
	txt = txt[1:]
    while txt and txt[-1] in '# \t':
	txt = txt[:-1]
    return txt

def sanitize(txt):
    '''Replace all "dangerous" characters (such as <>|\/")
    Also strip hashes and spaces at the beginning or end of the line
    '''
    txt = strip_hashes(txt)
    for c in ' \t<>/\|"\'?*:;~':
	txt = txt.replace(c, '-')
    return txt

# end of utils.py
