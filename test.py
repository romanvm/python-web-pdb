# coding: utf-8
from web_pdb import set_trace; set_trace()
import math
# Author: Roman Miroshnychenko aka Roman V.M.
# E-mail: romanvm@yandex.ua


foo = 'foo'
bar = 'bar'
unic = 'Тест'


def radius(r):
    rad = math.pi * r ** 2
    return rad

def tester(a, b):
    assert a == b


locs = locals()
rad = radius(10)
print(rad)
tester(foo, bar)
