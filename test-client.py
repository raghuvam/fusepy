#!/usr/bin/env python

import xmlrpclib,pickle
import datetime

import pprint

ttl = 3000

'''
def put(self, key, val, ttl):
    return self.caller.put(Binary(key), Binary(val), ttl)

def get(self, key):
    return self.caller.get(Binary(key))

def write_file(self, filename):
    return self.caller.write_file(Binary(filename))

def read_file(self, filename):
    return self.caller.read_file(Binary(filename))
'''

# method to store and retrieve any type of data on the server
def storeAndRetrieve(myserver,key,data):

   pickled_value = pickle.dumps(data) ## pickle data to be sent
   
   print "\n \nStoring and retrieving ", type(data)," with RPC"
   print "PUT: \nkey -> ",key, "\nvalue -> ",data ## print data
   
   ## put the data in HT with key as type name. Eg: key-"integer" data-1000
   myserver.put(xmlrpclib.Binary(key), xmlrpclib.Binary(pickled_value), ttl)
   print "\n"
   print "GET: key ->", key
   # retrieve data from the server
   rv = myserver.get(xmlrpclib.Binary(key)) 

   pprint.pprint(rv)
   ## print variable type of data recieved
   print "Type of the data received: ",type(pickle.loads(rv["value"].data))
   print "value.data: "
   ## unmarshall the data from server and pprint the data.
   pprint.pprint(pickle.loads(rv["value"].data))

def testWriteAndRead():
    return 0
   
   
   
def main():
   # setup client handle 
   myserver = xmlrpclib.ServerProxy("http://127.0.0.1:51234")
   
   storeAndRetrieve(myserver,"integer",2015)

   storeAndRetrieve(myserver,"string","hello world")
   
   storeAndRetrieve(myserver,"list",["this","is","a","list"])
   
   dic = {"/":{"/dir1":{"file1":"this is file1",
                            "/dir3":{}
                            },
                   "/dir2":{"/dir4":{"file2":"This is file2"}
                           }
                  }
         }
   
   storeAndRetrieve(myserver,"dictionary",dic)
   
   print "\n\n"
   #filename
   
   myserver.write_file(fh,xmlrpclib.Binary("file1"))
   myserver.read_file(fh,xmlrpclib.Binary("file1"))
   
   
   

if __name__ == "__main__":
  main()




