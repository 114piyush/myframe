import sys
import os
import os.path
import shutil
import platform
import re
import multiprocessing
import time
import random
import json
import code
import threading
import thread
import glob
import logging
import traceback

from urllib import urlopen, urlretrieve

from log import Log
from misc import Display, IgnoreCtrlC
from exceptions import TestManagerError
from collections import deque
from pprint import pprint
from importlib import import_module
from vmware.vcenter import VirtualCenter

class TestManager():
   '''Manager for managing all test cases.'''

   def __init__(self, cfg):
      self.cfg = cfg
      self.opts = cfg.opts
      self.log = cfg.logObj.log
      self.logDir = cfg.opts.logDir
      self.timelabel = cfg.timelabel
      self.ctrlC = False
      self.result = None
      self.moduleError =  None
      self.timeout = 60*60
      self.vc = [] # Multiple VC with Service Instance
      self.ssapp = [] # Multiple SSAPP

   def TimeoutFunc(self):
      '''Function invoked by timer thread in case of timeout '''
      self.log.debug("Timeout thread invoked now for test %s" % self.name)
      self.isTimeout = True
      #Interrupt test process
      thread.interrupt_main()

   def GetTestArgs(self, test):
       args = {}
       args['vc'] = self.vc
       args['ssapp'] = self.ssapp
       args['cfg'] = self.cfg
       args['testOption'] = self.cfg.opts.testOption
       # Seperate log for test case
       args['logObj'] = Log(filename='coho-log-'+test.moduleName,
	                    logDir=self.opts.logDir,
	                    consoleOutput=self.opts.debugMode)
       return args

   def ConnectAllVC(self):
       '''Function to connect all VCs and store their python objects in list'''
       for vcIP in self.opts.vcHosts.split(','):
           user = self.opts.vcUser
	   password = self.opts.vcPwd
	   try:
               vc = VirtualCenter(self.log, IP=vcIP, user=user,
	                          password=password)
	   except Exception as e:
               self.log.exception('Test exception: %(e)s', {'e': e})
	       raise Exception('VC Connection Error')
	   self.vc.append(vc)

   def DisconnectAllVC(self):
       '''Function to disconnect all VCs'''
       while self.vc:
           vc = self.vc.pop()
	   vc.DisconnectVC()

   def ConnectAllSSAPP(self):
       '''Function to connect all SSAPPs and store their python object in list'''
       pass

   def RunTest(self):
      test = self.cfg.testToRun

      #Initialize timer for test
      timer = threading.Timer(float(self.timeout),self.TimeoutFunc)
      module = None
      try:
         self.log.debug('Importing %(module)s...', {'module': test.moduleName})
         #module = import_module('coho.tests.'+test.name)
	 # Import from testDir TODO: Improve more
         module = __import__(test.moduleName, globals(), locals())
      except (SyntaxError, ImportError) as e:
         Display('Error importing test module: %(e)s', {'e': e})
         self.log.debug('Error importing test module: %(e)s', {'e': e})
         self.result = 'SETUPFAIL'
         self.moduleError = True

      if not self.result and 'Run' not in dir(module):
         Display("No 'Run()' method found in the '%s' module." % test.name)
         self.log.debug("No 'Run()' method found in the '%s' module." % self.name)
         self.result = 'SETUPFAIL'
         self.moduleError = True

      if not self.moduleError:
         try:
            self.log.info('Starting test %s...' % test.name)
            self.startTime = int(time.time())
            timer.start()

         except KeyboardInterrupt:
            if self.isTimeout == True:
               self.setupfail = True
               self.result = 'TIMEOUT'
            else:
               #Ctrl+C hit by user
               self.result = 'ABORT'
         except Exception as e:
            self.log.exception('Test exception while setup : %(e)s', {'e': e})
            # Test failed during setup , cancelling timer thread created for tracking timeout
            timer.cancel()
            self.result = 'SETUPFAIL'

      if not self.result:
         try:
	    # Connect all VCs before starting test
	    if self.opts.vcHosts:
	        self.ConnectAllVC()
	    # Connect All SSAPP before starting test
	    if self.opts.ssappHosts:
	        self.ConnectAllSSAPP()
	    # Define args to pass on test case
	    args = self.GetTestArgs(test)
            self.result = module.Run(args)  # Run the test
            self.result = 'PASS'
            self.duration = int(time.time()) - self.startTime
            self.log.info('Completed the test %s in %s sec' % (test.name, self.duration))
	    self.DisconnectAllVC()
            #Test already completed, cancelling timer thread created for tracking timeout
            timer.cancel()
         except KeyboardInterrupt:
            if self.isTimeout == True:
               self.result = 'TIMEOUT'
            else:
            #Ctrl+C hit by user
               self.result = 'ABORT'

         except Exception as e:
            # Test completed with an error, cancelling timer thread created for tracking timeout
            timer.cancel()
	    self.DisconnectAllVC()
            self.result = 'FAIL'
            self.log.exception('Test exception: %(e)s', {'e': e})
	    raise

