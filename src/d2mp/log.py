'''
Created on 01.06.2014

@author: Schleppi
'''
from d2mp import GET_ENV

import logging
if GET_ENV() == "dev":
    level = logging.DEBUG
else:
    level = logging.WARNING
    
logging.basicConfig(filename='d2mp.log', level = level, format='%(levelname)s - %(funcName)s - %(message)s')
logging.info("========= new programm start =========")
WARN = logging.warning
INFO = logging.info
DEBUG = logging.debug
ERROR = logging.error
CRITICAL = logging.critical