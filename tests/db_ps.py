# coding: utf-8
# Author: Roman Miroshnychenko aka Roman V.M.
# E-mail: romanvm@yandex.ua

from __future__ import print_function
import os
import sys

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(basedir)

try:
    input = raw_input
except NameError:
    pass

from web_pdb import set_trace; set_trace(patch_stdstreams=True)
foo = input('Enter something: ')
print('You have entered: ' + foo)
