from framework.config import Config
from framework.exceptions import *
from framework.misc import Display
import os
import sys
from framework.testmanager import TestManager

def Main():
   ret_code = 0
   try:
      # Get testing configuration
      config = Config()
      config.CheckOptions()
      from pprint import pprint
      #pprint(config)

      testManager = TestManager(config)

      config.logObj.log.debug('Calling testManager.RunTests')
      testManager.RunTest()
      result = testManager.result
      if result == "ABORT" or result == "FAIL" or result == "TIMEOUT" or result == "SKIP":
         # Not a clean pass.
         ret_code = 1
      config.logObj.log.debug('testManager.RunTests done')

   except (LogError, ConfigError, VCError, ImportError) as e:
      try:
         print 'Main:ERROR: %s' % str(e)
         config.logObj.log.error(str(e))
      except (UnboundLocalError, AttributeError):
         pass
      ret_code = 2

   except KeyboardInterrupt:
      ret_code = 3

   finally:
      try:

         # Delete pyVpx/testware if we extracted it from the VC build
         if config.logObj:
            config.logObj.log.debug('Calling CleanupPrereqs')

         if config.logObj:
            config.logObj.log.debug('CleanupPrereqs done')

      except UnboundLocalError:
         ret_code = 4
   return ret_code
