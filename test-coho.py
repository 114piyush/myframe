#!/usr/bin/env python

import sys
import platform
import os

if __name__ == '__main__':
   # Include lib path
   sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
   import coho
   ret_code = coho.Main()
   sys.exit(ret_code)
