from framework.config import Config
from framework.exceptions import *
from framework.misc import Display
import os
import sys

def Main():
   ret_code = 0
   try:
      # Get testing configuration
      config = Config()
      config.CheckOptions()

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
