# coding: utf-8
# Author: Roman Miroshnychenko aka Roman V.M.
# E-mail: roman1972@gmail.com
#
# Copyright (c) 2016 Roman Miroshnychenko
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import pprint
from pdb import Pdb


class PdbPy2(Pdb):
    """
    This class overrides ``do_p`` and ``do_pp`` methods
    to enable human-readable printing of Unicode strings in Python 2
    """
    def do_p(self, arg):
        try:
            repr_value = repr(self._getval(arg))
            # Try to convert Unicode string to human-readable form
            try:
                repr_value = repr_value.decode('raw_unicode_escape')
            except UnicodeError:
                repr_value = repr_value.decode('utf-8', 'replace')
            print >> self.stdout, repr_value
        except:
            pass

    def do_pp(self, arg):
        try:
            repr_value = pprint.pformat(self._getval(arg))
            # Try to convert Unicode string to human-readable form
            try:
                repr_value = repr_value.decode('raw_unicode_escape')
            except UnicodeError:
                repr_value = repr_value.decode('utf-8', 'replace')
            print >> self.stdout, repr_value
        except:
            pass
