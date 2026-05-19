# coding: utf-8
# Created on: 13.09.2016
# Author: Roman Miroshnychenko aka Roman V.M.

import os
import sys

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(basedir)

ustr = 'Тест'
foo = 'foo'
from web_pdb import set_trace; set_trace()
bar = 'bar'
ham = 'spam'
name = 'Монти'


def func(spam):
    print(spam)


func(ham)
