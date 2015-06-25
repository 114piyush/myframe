import sys
import os
import os.path
import time
import re
import random
import yaml

from log import Log
from ssh import *
from misc import Cache, IsWindows, Makedirs, Display
from exceptions import ConfigError
from argparse import ArgumentParser

class Test(object):
   def __init__(self, path):
      self.path = path
      self.desc = 'Test description:'
      self.timeout = 1800

      if path:
         # Relative path to python file from coho/tests
         name = path.rsplit(os.path.join(os.path.sep, 'tests'))[1]
         name = name.lstrip(os.path.sep)
         self.name = name

         # Module name for importing
         name = name.split('.')[0].replace(os.sep, '.')
         self.moduleName = name

         # Short name for display, and for __import__()
         name = name.rsplit('.', 1)[1] if '.' in name else name
         self.shortName = name


class Config(object):
   '''Manage CLI options and test configuration.'''

   def __init__(self):
      self.logObj = None
      self.timelabel = int(time.time())
      self.pid = os.getpid()
      self.opts = self.GetOptions()
      self.errors = []
      self.warnings = []

   def GetOptions(self):
      '''Get all CLI options.'''

      usage = '''
   Usage:
      '''
      conf_parser = ArgumentParser(add_help=False)

      #Config file parser option
      args, remaining_argv = conf_parser.parse_known_args()

      parser = ArgumentParser(usage=usage, parents=[conf_parser])

      if len(sys.argv) < 2:
         parser.print_usage()
	 sys.exit(1)

      parser.add_argument('-l', '--list', action='store_true', dest='listTests',
                        help='list all tests')
      testGroup = parser.add_argument_group('Tests')
      testGroup.add_argument('-t', '--test', dest='testCase',
                           help='test case option')
      parser.add_argument_group(testGroup)

      vcGroup = parser.add_argument_group('VC')
      vcGroup.add_argument('--vc-hosts', dest='vcHosts', default=[], metavar='IP1[,IP2,..]',
                          help='host or IP of VC to use for these tests. Comma seprated multiple VC host can be specified')
      vcGroup.add_argument('--vc-user', dest='vcUser', metavar='USER')
      vcGroup.add_argument('--vc-pwd', dest='vcPwd', metavar='PWD')
      parser.add_argument_group(vcGroup)

      vcGroup = parser.add_argument_group('SSAPP')
      vcGroup.add_argument('--ssapp-hosts', dest='ssappHosts', default=[], metavar='IP1[,IP2,..]',
                          help='host or IP of SSAPP to use for these tests. Comma seprated multiple SSAPP host can be specified')
      vcGroup.add_argument('--ssapp-user', dest='vcUser', metavar='USER')
      vcGroup.add_argument('--ssapp-pwd', dest='vcPwd', metavar='PWD')
      parser.add_argument_group(vcGroup)

      envGroup = parser.add_argument_group('Environment')
      envGroup.add_argument('--username', dest='username',
                            help='defaults to the USER env variable',
			    default=os.environ.get('USER') or os.environ.get('USERNAME'))
      envGroup.add_argument('--log-dir', dest='logDir', metavar='DIR',
                          help='overrides /tmp or C:\\tmp')
      envGroup.add_argument('--tests-dir', dest='testsDir', metavar='DIR',
                          help='overrides the TESTSDIR env variable or the ' \
                               'auto-discovered "tests" dir')
      parser.add_argument_group(envGroup)

      rtGroup = parser.add_argument_group('Runtime')
      rtGroup.add_argument('--debug-mode', action='store_true',
                         dest='debugMode',
                         help='put logs in console to make debug easy')
      rtGroup.add_argument('--no-run', dest='noRun', action='store_true',
                         help='just print what tests would be run')
      parser.add_argument_group(rtGroup)

      testGroup = parser.add_argument_group('TestOption')
      testGroup.add_argument('--test-option', dest='testOption', metavar='key:val[,key:val]',
                         help='additional option used for parameters')
      parser.add_argument_group(testGroup)

      opts = parser.parse_args(remaining_argv)

      return opts

   def CheckOptions(self):
      '''Check, scrub, and verify CLI options.'''

      self.logObj = Log(logDir=self.opts.logDir,
                        consoleOutput=self.opts.debugMode)
      Display('Logs: %s' % self.logObj.logDir)


      if not self.opts.testsDir:
         self.opts.testsDir = self.GetDirPath('TESTSDIR',
                                               os.path.join('coho', 'tests'))
      if not os.path.exists(self.opts.testsDir):
         self.errors.append('tests dir does not exist: %s' % self.opts.testsDir)
      sys.path.append(self.opts.testsDir)

      if self.opts.noRun:
         self.ListTestToRun()
      if self.opts.listTests:
         self.ListAllTests()
      self.ScrubOptions()
      if self.errors:
         raise ConfigError(self.errors)

      if self.warnings:
         Display('Warnings: %s' % '\n'.join(self.warnings))

   def GetDirPath(self, envName, pathEnding):
      '''Get the absolute path to the test directory.'''
      # Try to use an environment variable first.
      envValue = os.environ.get(envName)
      if envValue:
         if os.path.exists(envValue):
            return envValue
         else:
            self.errors.append('%s environment value of %s does not exist' % \
                               (envName, envValue))
      # Try to auto-discover the directory.
      splitStr = '%s%s%s' % (os.path.sep, 'lib', os.path.sep)
      baseDir = os.path.realpath(__file__).rsplit(splitStr, 1)[0]
      testDirPath = os.path.join(baseDir, pathEnding)

      return testDirPath

   def ListTestToRun(self):
      '''Used to check and print test.'''
      if not self.testToRun:
         print 'No tests would run'
      else:
         print 'The following test would be run:'
         print '  * %s ' % (self.testToRun.name)
         print
         sys.exit(0)

   def ListAllTests(self):
      '''Used to check and print test.'''
      if not self.allTests:
         print 'No tests would run'
      else:
         print 'The following tests present:'
	 for test in self.allTests:
            print '  * %s ' % (test.name)
         print
         sys.exit(0)

   def ScrubOptions(self):
      if not IsWindows():
         import pwd
         pw = pwd.getpwnam(self.opts.username)
         os.setuid(pw.pw_uid)

      bottomLogDir = 'coho-log-%s-%s-%s' % (self.opts.username, self.timelabel,
                                            self.pid)
      # Convert test options to dictionary
      if self.opts.testOption:
         testoption = self.opts.testOption.replace(':', ': ')
	 self.opts.testOption = yaml.load('{' + testoption + '}')
      if not self.opts.logDir:
         baseDir = 'C:\\temp' if IsWindows() else '/tmp'
         self.opts.logDir = os.path.join(baseDir, bottomLogDir)
      else:
         self.opts.logDir = os.path.join(self.opts.logDir, bottomLogDir)
      try:
         Makedirs(self.opts.logDir)
      except OSError as e:
         self.errors.append('Unable to create log dir %s: %s' % \
                            (self.opts.logDir, e))

   @Cache
   def testToRun(self):
      '''Determine which test to run based on CLI options.'''
      testcase = self.opts.testCase.replace('.','/') + '.py'
      for test in self.allTests:
         if test.name == testcase:
	    return test

   @Cache
   def allTests(self):
      '''Find all .py files in the tests dir'''
      tests = []
      for path, dirs, files in os.walk(self.opts.testsDir):
         for filename in files:
            if filename.endswith('.py') and filename != '__init__.py':
               test = Test(os.path.join(path, filename))
               tests.append(test)
      return tests
