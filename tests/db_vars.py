import os
import sys

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(basedir)


class Foo:
    def __init__(self):
        self.spam = 'eggs'
        self.items = ['ham']


foo = Foo()
data = {'key': 'value'}
from web_pdb import set_trace; set_trace()
bar = 'bar'
baz = 'baz'
