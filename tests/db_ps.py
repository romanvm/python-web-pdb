# coding: utf-8
# Author: Roman Miroshnychenko aka Roman V.M.

import os
import sys

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(basedir)

from web_pdb import set_trace; set_trace(patch_stdstreams=True)
foo = input('Enter something: ')
print('You have entered: ' + foo)
