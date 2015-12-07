#!/usr/bin/env python
import logging
from collections import defaultdict
from errno import ENOENT
from stat import S_IFDIR, S_IFLNK, S_IFREG
from sys import argv, exit
from time import time
import datetime
from fuse import FUSE, FuseOSError, Operations, LoggingMixIn
from xmlrpclib import Binary
import sys, pickle, xmlrpclib
import signal

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn
import hashlib

def put_fault_handler(fservers,path,key,value):
    #handle failed puts
    print "Put fault handler is handling...."
    count = len(fservers)-1
    while count > -1:
        try:
            if fservers[count].put(Binary(key),Binary(pickle.dumps(value)),6000) == True:
                fservers.pop(count)
                count = count -1
        except:
            time.sleep(1)
            continue
    print "PUT handler successful"
    return None

def update_checksum(meta_server,path,key,pickled_value):
    key = path +key+"&&checksum"
 
    dat_checksum = hashlib.md5(pickled_value).hexdigest()
    #put checksum on the meta server\
    meta_server.put(Binary(key),Binary(dat_checksum),6000)


def validate_checksum(meta_server,data_servers,path,key,rdata):
	fkey = path + key+"&&checksum"
	key = path + "&&" + key
	valid_checksum = meta_server.get(Binary(fkey))
	print valid_checksum, path, fkey
	valid_checksum = valid_checksum["value"].data
	print valid_checksum

	# checks if any server has corrupted data
	count = 0
	isCorrupted  = False
	print rdata
	for ndat in rdata:
		curr_checksum = hashlib.md5(ndat).hexdigest()
		print "server ",count," ",curr_checksum
		print "data ",pickle.dumps(ndat)
		if valid_checksum != curr_checksum:
			print "valid_checksum"
			print "Data server",count," is corrupted"
			failed_server_id = count
			isCorrupted = True
		if valid_checksum == curr_checksum:
			print "date_server ", count," is good"
            good_server_id = count
        count = count +1
    # correct the corrupted        	
    if isCorrupted:
        dh = xmlrpclib.Server(data_servers[failed_server_id])
        dh.put(Binary(key),Binary(rdata[good_server_id]),6000)
	
    return  pickle.loads(rdata[good_server_id])

        '''
        print "Correcting corrupted data" 
        print "good_server_id: ",good_server_id
        print "failed_server_id: ",failed_server_id
        print "good data: ",rdata[good_server_id]
        print "unpickeld good data: ",pickle.loads(rdata[good_server_id])
        print "bad data: ",rdata[failed_server_id]
        '''


class ReliableLayer:
    def __init__(self,urls):        
        self.urls = urls        
        self.meta_url = urls[0]
        self.data_urls = urls[1:]

        self.Qw = 0;
        self.Qr = 0;

        # getting meta server handlers
        self.meta_hdl = xmlrpclib.Server(self.meta_url)
        # setting up data server handlers
        self.data_hdls = []
        failed_servers = []        
        
    
            

    def reliable_put(self,path,key,value):
        pickled_value = pickle.dumps(value)
        if key == "meta" or key == "list_nodes":
            key = path +"&&" + key
            self.meta_hdl.put(Binary(key),Binary(pickled_value),6000)
        else:
            
            update_checksum(self.meta_hdl,path,key,pickled_value)
            count = 0
            #contains handlers for failed puts
            failed = []
            key = path + "&&" + key
            check = False

            for url in self.data_urls:
                isConnected = False
                while isConnected == False:
                    try:
                        # try to connect to the server
                        dh = xmlrpclib.Server(url)
                        dh.put(Binary(key),Binary(pickled_value),6000)
                        isConnected = True
                    except:
                        #print "appending fault servers list"
                        time.sleep(1)
                        print "Trying to reconnect to the server"
                        continue
            '''
            for dh in self.data_hdls:
                try:
                    check = dh.put(Binary(key),Binary(pickled_value),6000)
                except:
                    #print "appending fault servers list"
                    failed.append(dh)
                    if len(failed) > self.Qw:
                put_fault_handler(failed,path,key,pickled_value)
            '''
            
                
    def reliable_get(self,path,key):    
        
        if key == "meta" or key == "list_nodes":
            key = path+"&&"+key
            res = self.meta_hdl.get(Binary(key))
            if "value" in res:
                return pickle.loads(res["value"].data)
            else:
                return None

        else:
            tkey = key
            key = path +"&&" + key
            
            #Append data recieved from server to rdata
            rdata = []
            isConnected = False
            for url in self.data_urls:
                isConnected = False
                while isConnected == False:
                    try:
                        # try to connect to the server
                        dh = xmlrpclib.Server(url)
                        res = dh.get(Binary(key))
                        # append to rdata
                        if "value" in res:
                            rdata.append(res["value"].data)
                        isConnected = True
                    except:
                        #print "appending fault servers list"
                        time.sleep(1)
                        print "Trying to reconnect to the server"
                        continue
            '''
            for dh in self.data_hdls:
            	res = dh.get(Binary(key))
            	# append to rdata
            	if "value" in res:
                	rdata.append(res["value"].data)
            '''
            if len(rdata) == 0:
            	return None

            # validate checksum
            result  =validate_checksum(self.meta_hdl,self.data_urls,path,tkey,rdata)

            return result
           
