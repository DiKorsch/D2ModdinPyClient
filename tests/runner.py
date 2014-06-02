'''
Created on 01.06.2014

@author: Schleppi

Usage: 
  ./runner.py                     -> executes all tests
  ./runner.py <TestCaseClass>     -> executes only tests from this testcase
'''
import unittest, sys

sys.path.append("../src")
from steamtests import *
from mod_manager_tests import *


if __name__ == "__main__":
    unittest.main()