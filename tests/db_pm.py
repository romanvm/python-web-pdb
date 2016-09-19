# coding: utf-8
# Created on: 16.09.2016
# Author: Roman Miroshnychenko aka Roman V.M. (romanvm@yandex.ua)


import os
import sys

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(basedir)
import web_pdb

with web_pdb.catch_post_mortem():
    assert False, 'Oops!'
