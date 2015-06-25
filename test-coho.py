#!/usr/bin/env python

import sys
import platform
import os

if __name__ == '__main__':
   # Include lib path
   sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
   sys.path.append(os.path.join(os.path.dirname(__file__), 'pyvmomi'))
   import cohotest
   ret_code = cohotest.Main()
   sys.exit(ret_code)
