import sys
import os
import re
import platform
import errno
import multiprocessing
import time
import random
import signal
import subprocess
import Queue
from functools import wraps
from  framework.exceptions import TimeoutError
import tarfile

# Functions

def IsWindows():
   return platform.system() == 'Windows'

def Makedirs(path):
   try:
      os.makedirs(path)
   except OSError as e:
      if e.errno == errno.EEXIST:
         pass
      else:
         raise

def Display(msg, newLine=True, eraseLine=True):
   if eraseLine:
      msg = '\r%s' % msg
   if newLine:
      print msg
   elif sys.stdout.isatty():
      sys.stdout.write(msg)
      sys.stdout.flush()

def TerminateProcesses(processes, timeout=0):
   for process in processes:
      process.join(timeout)
      if process.is_alive():
         process.terminate()

class LocalProcess(multiprocessing.Process):
   '''Process object that runs a command locally'''

   def __init__(self, cmd, executable=None, queue=None, errQueue=None, env=None):
      multiprocessing.Process.__init__(self)
      self.cmd = cmd
      self.executable = executable
      self.queue = queue
      self.errQueue = errQueue
      self.env = env
      self.cmd_return_code = multiprocessing.Value("i", -1)

   def run(self):
      '''
      Override multiprocessing.Process's run() method with our own that
      executed a command locally
      '''

      if self.cmd:
         process = subprocess.Popen(self.cmd.split(), executable=self.executable,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    env=self.env)
         stdout, stderr = process.communicate()

         self.queue.put(stdout.strip())
         self.errQueue.put(stderr.strip())
         self.cmd_return_code.value = process.returncode

         if process.returncode != 0:
            sys.stdout.write('cmd failed: %s\n' % self.cmd.split())
            sys.stdout.write(stdout)
            sys.stdout.write(stderr)


def RunCmdLocally(cmd, timeout=15, env=None, cmd_return_code=False):
   '''Wrapper for LocalProcess() to run a single command'''

   stdout, stderr = '', ''
   stdoutQueue = multiprocessing.Queue()
   stderrQueue = multiprocessing.Queue()
   process = LocalProcess(cmd, queue=stdoutQueue, errQueue=stderrQueue, env=env)
   try:
      process.start()
      process.join(timeout)
      if process.is_alive():
         process.terminate()

      stdout = stdoutQueue.get(True, timeout)
      stderr = stderrQueue.get(True, timeout)
   except (KeyboardInterrupt, Queue.Empty):
      if process.is_alive():
         process.terminate()

   if cmd_return_code:
       return process.exitcode, stdout, stderr, process.cmd_return_code.value
   else:
       return process.exitcode, stdout, stderr

# Decorators

class Cache(object):
   '''Decorator class to cache expensive method calls.'''

   def __init__(self, cache_function):
      self._cache = cache_function

   def __get__(self, obj, _=None):
      if obj is None:
         return self
      value = self._cache(obj)
      setattr(obj, self._cache.func_name, value)
      return value


def IgnoreCtrlC(func):
   '''Disable Ctrl-C before the function call; re-enable it after.'''

   def PrintCtrlcMsg(*args):
      print 'Ctrl-C is disabled during clean-up and other critical operations.'

   def OriginalFunctionIgnoringCtrlC(*args):
      ctrlcHandler = signal.signal(signal.SIGINT, PrintCtrlcMsg)
      f = func(*args)
      signal.signal(signal.SIGINT, ctrlcHandler)

   return OriginalFunctionIgnoringCtrlC

def timeout(seconds=10, error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator
