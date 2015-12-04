#!/usr/bin/env python

import logging

from collections import defaultdict
from errno import ENOENT
from stat import S_IFDIR, S_IFLNK, S_IFREG
from sys import argv, exit
from time import time

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn

if not hasattr(__builtins__, 'bytes'):
    bytes = str

############################
### RV: custom functions ###
############################

### split path to keys###

def splitPath(spath):
 
  print "split path"
  if spath == '/':  
      return list('/')
  else:
      mapList = spath.split('/')
      #mapList.remove('')
      mapList=['/' + x for x in mapList]
      #print mapList
      return mapList

### make path from list of keys ###
def makePath(plist):    
    print "make path"
    nlist  = []
    
    for x in plist: nlist.append(x[1:])        
      
    npath =  '/'.join(nlist)
    
    #npath = '/' +npath
    print "npath"
   
    if npath == '':
        npath = '/'
    #print npath
    
    return npath

### get file from dictionary ###


def getFileDict(fileDict, fpath): ## rv check path       
     
     if not isinstance(fpath,list):
         mapList = splitPath(fpath)
     else:
         mapList = fpath
     
     print "get file"
     print mapList    
         
     rfiles = reduce(lambda d, k: d[k]["childnodes"], mapList, fileDict)
     
     print rfiles 
     return rfiles


def setNodeDict(fileDict, spath, value): ## set path    
    
    # if not isinstance(spath,list):
    #     mapList = splitPath(spath)
    # else:
    #     mapList = spath   
     
     mapList = splitPath(spath)
     
     print "setFile"
     print mapList 
     
     if spath == '/':
          fileDict["/"] = value
    # elif len(mapList) == 1:
     #     fileDict[mapList[0]]["metadata"] = value
     #     fileDict[mapList[0]]["childnodes"] = {}
     else:
          par_dir ={} 
          print mapList[-1]
          par_dir_childnodes = getFileDict(fileDict, makePath(mapList[:-1]))
          par_dir_childnodes[mapList[-1]] = value
          


def getParentDict(fileDict, spath): ## gets the key to parent directory   
     
     mapList = splitPath(spath)
     
     print "setFile"
     print mapList 
     
     if spath == '/':
          return None
     else:
          return getCurNode(fileDict, makePath(mapList[:-1]))         
          
def getCurNode(fileDict, spath): ## gets the key to parent directory   
     
     mapList = splitPath(spath)
     
     print "get current file"
     print mapList 
     
     if spath == '/':
          return fileDict['/']
     else:
          print "cur_file:", mapList[-1]
          cur_file = getFileDict(fileDict, makePath(mapList[:-1]))[mapList[-1]]
          print "CURR FILE DICT" , cur_file
          return cur_file      
          
def popFileDict(fileDict,spath):
     
     mapList = splitPath(spath)
     
     print "setFile"
     print mapList 
     
     if spath == '/':
          return None
     else:
          par_dir= getCurNode(fileDict, makePath(mapList[:-1]))  
          popedFile = par_dir["childnodes"].pop(mapList[-1])
          return popedFile      
          
def pathCheck(fileDict,spath):
    
    print "path check"
    print spath
    print fileDict
    try:
      getCurNode(fileDict,spath)
      return True
    except:
      return False

######
######

class Memory(LoggingMixIn, Operations):
    'Example memory filesystem. Supports only one level of files.'

    def __init__(self):
        self.files = {}
        self.data = defaultdict(bytes)
        self.fd = 0
        now = time()
        self.files['/'] = {"metadata":{},"childnodes":{},"data":list()}
        self.files['/']["metadata"] = dict(st_mode=(S_IFDIR | 0755), st_ctime=now,
                               st_mtime=now, st_atime=now, st_nlink=2)

    def chmod(self, path, mode):
        curFile = getCurNode(self.files,path) #rv
        curFile["metadata"]['st_mode'] &= 0770000 #rv
        curFile["metadata"]['st_mode'] |= mode    #rv
        return 0

    def chown(self, path, uid, gid):
        curFile = getCurNode(self.files,path) #rv
        curFile["metadata"]['st_uid'] = uid
        curFile["metadata"]['st_gid'] = gid

    def create(self, path, mode):
    
        data = {}
        data["metadata"] = dict(st_mode=(S_IFREG | mode), st_nlink=1,
                                st_size=0, st_ctime=time(), st_mtime=time(),
                                st_atime=time())
        data["childnodes"] = {}                       
        data["data"] = list()
        
        setNodeDict(self.files,path,data)       
               
        self.fd += 1
        return self.fd

    def getattr(self, path, fh=None):
        print "GETT ATTRS of file: ",path
        if not pathCheck(self.files,path):#Check if the file exist using pathCheck() rv
            raise FuseOSError(ENOENT)
      
        return getCurNode(self.files,path)["metadata"] #rv

    def getxattr(self, path, name, position=0):
        
        print "attr name"
        print name
        print "xattr position"
        print position
        
        curFile = getCurNode(self.files,path)
        attrs = curFile["metadata"].get('attrs', {})

        try:
            return attrs[name]
        except KeyError:
            return ''       # Should return ENOATTR

    def listxattr(self, path):
        curFile = getCurNode(self.files,path) #rv
        attrs = curFile["metadata"].get('attrs', {})
        return attrs.keys()

    def mkdir(self, path, mode):
        data = { "metadata": dict(st_mode=(S_IFDIR | mode), st_nlink=2,
                                st_size=0, st_ctime=time(), st_mtime=time(),
                                st_atime=time()),"childnodes": dict(),"data":list()}
        
        print "MKDIR", path
        setNodeDict(self.files,path,data)
        
        
              
        getParentDict(self.files,path)["metadata"]['st_nlink'] += 1

    def open(self, path, flags):
        self.fd += 1
        return self.fd

    def read(self, path, size, offset, fh):
        curFile= getCurNode(self.files,path)
        datalist = curFile["data"][offset:offset + size]
        datastring = ''.join(datalist)
        return datastring
    def readdir(self, path, fh):
        curFile = getCurNode(self.files,path)["childnodes"]
        return ['.', '..'] + [x[1:] for x in curFile if x != '/'] ## rv: DOUBT ##

    def readlink(self, path):
        curFile = getCurNode(self.files,path)
        return curFile["data"]

    def removexattr(self, path, name):
        curFile=getCurNode(self.files,path) #rv
        attrs = curFile["metadata"].get('attrs', {})  #rv

        try:
            del attrs[name]
        except KeyError:
            pass        # Should return ENOATTR

    def rename(self, old, new):
         #rv
        
        if not pathCheck(self.files,old):  #Check if the file exist using pathCheck() rv
            raise FuseOSError(ENOENT)
        
        popedFile=popFileDict(self.files,old)
        setNodeDict(self.files,new,popedFile)
         
        #self.files[new] = self.files.pop(old)

    def rmdir(self, path):
        popFileDict(self.files,path)
        
        getParentDict(self.files,path)["metadata"]['st_nlink'] -= 1

    def setxattr(self, path, name, value, options, position=0):
        # Ignore options
        curFile=getCurNode(self.files,path) #rv
        
        attrs = curFile["metadata"].setdefault('attrs', {})
        attrs[name] = value

    def statfs(self, path):
        return dict(f_bsize=512, f_blocks=4096, f_bavail=2048)

    def symlink(self, target, source):
    
        file_dict ={"metadata": dict(st_mode=(S_IFLNK | 0777), st_nlink=1,
                                  st_size=len(source)),"childnodes" : {},"data":{}}
        
        setNodeDict(self.files,target,file_dict)
        
        curFile= getCurNode(self.files,target)
        
        curFile["data"]=source

    def truncate(self, path, length, fh=None):
        
        curFile=getCurNode(self.files,path)
        curFile["data"] = curFile["data"][:length]
        curFile["metadata"]['st_size'] = length

    def unlink(self, path):
        popFileDict(self.files,path)

    def utimens(self, path, times=None):
        now = time()
        atime, mtime = times if times else (now, now)

        curFile=getCurNode(self.files,path) #rv
        curFile["metadata"]['st_atime'] = atime
        curFile["metadata"]['st_mtime'] = mtime

    def write(self, path, data, offset, fh):
        curFile = getCurNode(self.files,path)
        curFile["data"] = curFile["data"][:offset]+ list(data)
        curFile["metadata"]['st_size'] = len(curFile["data"]) ## rv
        return len(data)


if __name__ == '__main__':
    if len(argv) != 2:
        print('usage: %s <mountpoint>' % argv[0])
        exit(1)

    logging.getLogger().setLevel(logging.DEBUG)
    fuse = FUSE(Memory(), argv[1], foreground=True,debug=True)
