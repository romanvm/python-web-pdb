# coding: utf-8
# Author: Roman Miroshnychenko aka Roman V.M.
# E-mail: romanvm@yandex.ua

import web_pdb

with web_pdb.catch_post_mortem():
    foo = 'foo'
    bar = 'bar'
    assert foo == bar
