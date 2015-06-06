# XXX: Can these be collapsed into one class that still prefixes the message
# with the exception type (e.g. 'Log Error', 'Config Error', etc)?
class LogError(Exception):
   def __init__(self, error):
      self.error = error

   def __str__(self):
      return 'Log Error: %s' % str(self.error)


class ConfigError(Exception):
   def __init__(self, errors):
      self.errors = errors

   def __str__(self):
      if isinstance(self.errors, basestring):
         return 'Config Error: %s' % str(self.errors)
      elif len(self.errors) == 1:
         return 'Config Error: %s' % str(self.errors[0])
      else:
         return '\n  Config Errors:%s' % \
                ''.join(['\n  * %s' % err for err in self.errors])


class TestManagerError(Exception):
   def __init__(self, error):
      self.error = error

   def __str__(self):
      return 'TestManager Error: %s' % str(self.error)

class VCError(Exception):
   def __init__(self, error):
      self.error = error

   def __str__(self):
      return 'VC Error: %s' % str(self.error)


class APIError(Exception):
   def __init__(self, error):
      self.error = error

   def __str__(self):
      return 'API Error: %s' % str(self.error)


class TestFailedError(Exception):
   def __init__(self, errors):
      self.errors = errors

   def __str__(self):
      if isinstance(self.errors, basestring):
         return 'Test failed: %s' % str(self.errors)
      elif len(self.errors) == 1:
         return 'Test failed: %s' % str(self.errors[0])
      else:
         return '\n  Test failed:%s' % \
                ''.join(['\n  * %s' % err for err in self.errors])

class InfraError(Exception):
   def __init__(self, error):
       self.error = error

   def __str__(self):
      return 'Infrastructure Error: %s' % str(self.error)


class ProductError(Exception):
   def __init__(self, error):
      self.error = error

   def __str__(self):
      return 'Product Error: %s' % str(self.error)


class TimeoutError(Exception):
   def __init__(self, error):
      self.error = error

   def __str__(self):
      return 'Timeout Error: %s' % str(self.error)
