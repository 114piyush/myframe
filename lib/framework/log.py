import sys
import os.path
import time
import logging

from exceptions import LogError
from misc import IsWindows, Makedirs


class Log(object):
   def __init__(self, filename='coho-main.log', logDir='', testname='',
                consoleOutput=False):
      if not filename.startswith('coho-main'):
         raise LogError("log filename '%s' must start with 'coho-main'" \
                        % filename)
      self.filename = filename
      self.baseDir = 'C:\\temp' if IsWindows() else '/tmp'
      if not logDir:
         user = os.environ.get('USER') or os.environ.get('USERNAME') or 'noname'
         logDir = os.path.join(self.baseDir, 'coho-log-%s-%s-%s' % \
                               (user, int(time.time()), os.getpid()))
      Makedirs(logDir)
      self.logDir = logDir
      self.logPath = os.path.join(logDir, filename)
      self.name = os.path.splitext(filename)[0]

      # Create and configure the logger instance.
      self.logFormat = \
         logging.Formatter('%(asctime)s [%(levelname)s %(filename)s::'
                           '%(funcName)s::%(lineno)s] %(message)s')
      self.log = logging.getLogger(self.name)
      self.log.level = logging.DEBUG

      # Initialize, create, and add the log handlers
      self.streamHandler = None
      self.fileHandler = None

      self.CreateHandlers(consoleOutput)
      self.AddHandlers()

   def CreateHandlers(self, consoleOutput=False):
      '''Create a log file handler and optional log stream handler.'''

      # Output to console
      if consoleOutput:
         self.streamHandler = logging.StreamHandler()
         self.streamHandler.setLevel(logging.DEBUG)
         self.streamHandler.setFormatter(self.logFormat)

      # Log all messages to file
      self.fileHandler = logging.FileHandler(self.logPath)
      self.fileHandler.setLevel(logging.DEBUG)
      self.fileHandler.setFormatter(self.logFormat)

   def AddHandlers(self):
      '''Add handlers to a Log instance.'''

      self.log.addHandler(self.fileHandler)
      if self.streamHandler:
         self.log.addHandler(self.streamHandler)

   def RemoveHandlers(self):
      '''Remove all handlers from a Log instance.'''

      self.log.removeHandler(self.fileHandler)
      if self.streamHandler:
         self.log.removeHandler(self.streamHandler)
