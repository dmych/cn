# utils.py

def getProgramPath():
    import sys
    import os.path
    pname = sys.argv[0]
    if os.path.islink(pname):
        pname = os.readlink(pname)
    return os.path.split(pname)[0]

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
	    print 'CANNOT FIND', self.fileName
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
	print 'CONFIG'
	print self.data

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

# end of utils.py
