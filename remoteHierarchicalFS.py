#!/usr/bin/env python

import logging

from collections import defaultdict
from errno import ENOENT
from stat import S_IFDIR, S_IFLNK, S_IFREG
from sys import argv, exit
from time import time

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn
from xmlrpclib import Binary
import sys, pickle, xmlrpclib
import pprint
ttl =3000

if not hasattr(__builtins__, 'bytes'):
    bytes = str

############################
### RV: custom functions ###
############################

def putRpcDict(myserver,fileDict):
   key = "dictionary"
   pickled_value = pickle.dumps(fileDict) ## pickle data to be sent
   
   print "\n \nStoring and retrieving ", type(fileDict)," with RPC"
   print "PUT: \nkey -> ",key, "\nvalue -> ",fileDict ## print data
   
   ## put the data in HT with key as type name. Eg: key-"integer" data-1000
   myserver.put(xmlrpclib.Binary(key), xmlrpclib.Binary(pickled_value), ttl)
   print "\n"
   print "GET: key ->", key

def getRpcDict(myserver):
    
   rv = myserver.get(Binary("dictionary"))
    
   pprint.pprint(rv)
   ## print variable type of data recieved
   print "Type of the data received: ",type(pickle.loads(rv["value"].data))
   print "value.data: "
   ## unmarshall the data from server and pprint the data.
   return pickle.loads(rv["value"].data)

### split path to keys####

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


def setFileDict(fileDict, spath, value): ## set path    
    
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
          return getCurFile(fileDict, makePath(mapList[:-1]))         
          
def getCurFile(fileDict, spath): ## gets the key to parent directory   
     
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
          par_dir= getCurFile(fileDict, makePath(mapList[:-1]))  
          popedFile = par_dir["childnodes"].pop(mapList[-1])
          return popedFile      
          
def pathCheck(fileDict,spath):
    
    print "path check"
    print spath
    print fileDict
    try:
      getCurFile(fileDict,spath)
      return True
    except:
      return False

######
######

class Memory(LoggingMixIn, Operations):
    'Example memory filesystem. Supports only one level of files.'

    def __init__(self,url):
        self.files = {}
        self.myserver = xmlrpclib.ServerProxy(url)
        self.files['/'] = {"metadata":{},"childnodes":{},"data":list()}
        putRpcDict(self.myserver,self.files)
        self.data = defaultdict(bytes)
        self.fd = 0
        now = time()
        self.files['/'] = {"metadata":{},"childnodes":{},"data":list()}
        self.files['/']["metadata"] = dict(st_mode=(S_IFDIR | 0755), st_ctime=now,
                               st_mtime=now, st_atime=now, st_nlink=2)
        
        putRpcDict(self.myserver,self.files)
        

    def chmod(self, path, mode):
        fileDict = getRpcDict(self.myserver)
        curFile = getCurFile(fileDict,path) #rv
        curFile["metadata"]['st_mode'] &= 0770000 #rv
        curFile["metadata"]['st_mode'] |= mode    #rv
        putRpcDict(self.myserver,fileDict)
        
        return 0

    def chown(self, path, uid, gid):
        fileDict = getRpcDict(self.myserver)
        curFile = getCurFile(fileDict,path) #rv
        curFile["metadata"]['st_uid'] = uid
        curFile["metadata"]['st_gid'] = gid
        putRpcDict(self.myserver,fileDict)
        
    def create(self, path, mode):
    
        data = {}
        data["metadata"] = dict(st_mode=(S_IFREG | mode), st_nlink=1,
                                st_size=0, st_ctime=time(), st_mtime=time(),
                                st_atime=time())
        data["childnodes"] = {}                       
        data["data"] = list()
        
        fileDict = getRpcDict(self.myserver)
        setFileDict(fileDict,path,data)
        putRpcDict(self.myserver,fileDict)    
               
        self.fd += 1
        return self.fd

    def getattr(self, path, fh=None):
        fileDict = getRpcDict(self.myserver)
        print "GETT ATTRS of file: ",path
        if not pathCheck(fileDict,path):#Check if the file exist using pathCheck() rv
            raise FuseOSError(ENOENT)
      
        return getCurFile(fileDict,path)["metadata"] #rv

    def getxattr(self, path, name, position=0):
        fileDict = getRpcDict(self.myserver)
        print "attr name"
        print name
        print "xattr position"
        print position
        
        curFile = getCurFile(fileDict,path)
        attrs = curFile["metadata"].get('attrs', {})

        try:
            return attrs[name]
        except KeyError:
            return ''       # Should return ENOATTR

    def listxattr(self, path):
        fileDict = getRpcDict(self.myserver)
        curFile = getCurFile(fileDict,path) #rv
        attrs = curFile["metadata"].get('attrs', {})
        return attrs.keys()

    def mkdir(self, path, mode):
        data = { "metadata": dict(st_mode=(S_IFDIR | mode), st_nlink=2,
                                st_size=0, st_ctime=time(), st_mtime=time(),
                                st_atime=time()),"childnodes": dict(),"data":list()}
        
        print "MKDIR", path
        fileDict = getRpcDict(self.myserver)
        setFileDict(fileDict,path,data)
               
        getParentDict(fileDict,path)["metadata"]['st_nlink'] += 1
        
        putRpcDict(self.myserver,fileDict)
        

    def open(self, path, flags):
        self.fd += 1
        return self.fd

    def read(self, path, size, offset, fh):
        fileDict = getRpcDict(self.myserver)
        curFile= getCurFile(fileDict,path)
        datalist = curFile["data"][offset:offset + size]
        datastring = ''.join(datalist)
        return datastring
    def readdir(self, path, fh):
        fileDict = getRpcDict(self.myserver)
        curFile = getCurFile(fileDict,path)["childnodes"]
        return ['.', '..'] + [x[1:] for x in curFile if x != '/'] ## rv: DOUBT ##

    def readlink(self, path):
        fileDict = getRpcDict(self.myserver)
        curFile = getCurFile(fileDict,path)
        return curFile["data"]

    def removexattr(self, path, name):
        fileDict = getRpcDict(self.myserver)
        curFile=getCurFile(fileDict,path) #rv
        attrs = curFile["metadata"].get('attrs', {})  #rv

        try:
            del attrs[name]
            putRpcDict(self.myserver,fileDict)
        except KeyError:
            pass        # Should return ENOATTR

    def rename(self, old, new):
         #rv
        fileDict = getRpcDict(self.myserver)
        if not pathCheck(fileDict,old):  #Check if the file exist using pathCheck() rv
            raise FuseOSError(ENOENT)
        
        popedFile=popFileDict(fileDict,old)
        setFileDict(fileDict,new,popedFile)
        putRpcDict(self.myserver,fileDict)
         

    def rmdir(self, path):
        fileDict = getRpcDict(self.myserver)
        popFileDict(fileDict,path)
        
        getParentDict(fileDict,path)["metadata"]['st_nlink'] -= 1
        
        putRpcDict(self.myserver,fileDict)

    def setxattr(self, path, name, value, options, position=0):
        # Ignore options
        fileDict = getRpcDict(self.myserver)
        curFile=getCurFile(fileDict,path) #rv
        
        attrs = curFile["metadata"].setdefault('attrs', {})
        attrs[name] = value
        putRpcDict(self.myserver,fileDict)

    def statfs(self, path):
        return dict(f_bsize=512, f_blocks=4096, f_bavail=2048)

    def symlink(self, target, source):
        fileDict = getRpcDict(self.myserver)
        file_dict ={"metadata": dict(st_mode=(S_IFLNK | 0777), st_nlink=1,
                                  st_size=len(source)),"childnodes" : {},"data":{}}
        
        setFileDict(fileDict,target,file_dict)
        
        curFile= getCurFile(fileDict,target)
        
        curFile["data"]=source
        putRpcDict(self.myserver,fileDict)

    def truncate(self, path, length, fh=None):
        fileDict = getRpcDict(self.myserver)
        curFile=getCurFile(fileDict,path)
        curFile["data"] = curFile["data"][:length]
        curFile["metadata"]['st_size'] = length
        putRpcDict(self.myserver,fileDict)

    def unlink(self, path):
        fileDict = getRpcDict(self.myserver)
        popFileDict(fileDict,path)
        putRpcDict(self.myserver,fileDict)

    def utimens(self, path, times=None):
        fileDict = getRpcDict(self.myserver)
        now = time()
        atime, mtime = times if times else (now, now)

        curFile=getCurFile(fileDict,path) #rv
        curFile["metadata"]['st_atime'] = atime
        curFile["metadata"]['st_mtime'] = mtime
        putRpcDict(self.myserver,fileDict)

    def write(self, path, data, offset, fh):
        fileDict = getRpcDict(self.myserver)
        curFile = getCurFile(fileDict,path)
        curFile["data"] = curFile["data"][:offset]+ list(data)
        curFile["metadata"]['st_size'] = len(curFile["data"]) ## rv
        
        putRpcDict(self.myserver,fileDict)
        return len(data)


if __name__ == '__main__':
    if len(argv) != 3:
        print('usage: %s <mountpoint> <server-url>' % argv[0])
        exit(1)
    url = argv[2]
    logging.getLogger().setLevel(logging.DEBUG)
    fuse = FUSE(Memory(url), argv[1], foreground=True,debug=True)
