import xmlrpclib
from xmlrpclib import Binary

import unittest
import os
import subprocess
from subprocess import check_output
from subprocess import Popen, PIPE
from xmlrpclib import Binary
import sys, pickle, xmlrpclib
import signal
import subprocess
import threading


for port in sys.argv[2:]:
    url="http://localhost:"+port
    sh = xmlrpclib.Server(url)
    print "corrutped"
    sh.corrupt(Binary(sys.argv[1]))
