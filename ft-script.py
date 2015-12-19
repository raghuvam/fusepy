import sys, SimpleXMLRPCServer, getopt, pickle, time, threading, xmlrpclib, unittest
from datetime import datetime, timedelta
from xmlrpclib import Binary
from multiprocessing import Pool
import signal
import os
from subprocess import check_output
from subprocess import Popen, PIPE

#test 1
#sh = xmlrpclib.Server("http://localhost:51236")
#sh.terminate()
#time.sleep(10)


basepath = '/home/rv/junk/fusepy'
os.chdir(basepath)

cmd_line ="echo Opened New terminal"
meta = Popen(cmd_line, shell=True, stdin=PIPE)  # set environment, start new shell
meta.communicate("python metaserver.py 51234") # pass commands to the opened shell

ds = Popen(cmd_line, shell=True, stdin=PIPE)   # set environment, start new shell
ds.communicate("python dataserver.py 51235 51236") # pass commands to the opened shell
