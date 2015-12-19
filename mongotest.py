#!/usr/bin/env python
import logging
from collections import defaultdict
from errno import ENOENT
from stat import S_IFDIR, S_IFLNK, S_IFREG
from sys import argv, exit
from time import time
from time import time
import datetime
#from fuse import FUSE, FuseOSError, Operations, LoggingMixIn
#from xmlrpclib import Binary
import sys, pickle, xmlrpclib



count = 0

#from fuse import FUSE, FuseOSError, Operations, LoggingMixIn
from pymongo import MongoClient


def main():
      
      print "connecting to mongo"
      
      mongoc = MongoClient('127.0.0.1',27017)
      db = mongoc.test
      db.filesystem.remove()
      fdict = dict()

      key = "/dir3 && meta"
      value = dict()
      
      #file contents
      value["meta"] ={"st_link":1}
      value["data"]=[]
      value["list_nodes"]={}
      
      print "puting", key,value
      
      fdict[key] = value
      
      print fdict
      mfs = db.filesystem
      f1id = mfs.insert_one(fdict).inserted_id
      print "inserted id", f1id
      
      print db.collection_names(include_system_collections=False)
      
      ## get data
      print "get from filesystem"
      
      print "\n\n", mfs.find_one(f1id)
      
      ##################
      
      f1dict = dict()
      
      key = "/dir1/dir4 && meta"
      value = dict()
      
      #file contents
      value["meta"] ={"st_link":1}
      value["data"]=[]
      value["list_nodes"]={}
      
      print "puting ", key,value
      
      f1dict[key] = value
      
      print f1dict
      mfs = db.filesystem
      fid= mfs.insert_one(f1dict).inserted_id
      
      print fid
 
      ## get data
      print "get from filesystem"
      #print "dat file: ", fdict
      print "\n \n ",mfs.find_one({'_id':fid})
      print "\n\n", mfs.find_one(f1id)
      
      ########
      
      nd = dict()
      
      nd[]
      
      print "count ", mfs.count()
      
  
if __name__ == '__main__':
  main()





