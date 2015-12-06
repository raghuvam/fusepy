import sys, SimpleXMLRPCServer, getopt, pickle, time, threading, xmlrpclib, unittest
from datetime import datetime, timedelta
from xmlrpclib import Binary
from multiprocessing import Pool
import signal

#test 1
sh = xmlrpclib.Server("http://localhost:51236")
sh.terminate()
time.sleep(10)

