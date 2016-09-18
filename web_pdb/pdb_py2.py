# coding: utf-8
# Author: Roman Miroshnychenko aka Roman V.M.
# E-mail: romanvm@yandex.ua

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
                repr_value = repr_value.decode('raw_unicode_escape').encode('utf-8')
            except UnicodeError:
                pass
            print >> self.stdout, repr_value
        except:
            pass

    def do_pp(self, arg):
        try:
            repr_value = pprint.pformat(self._getval(arg))
            # Try to convert Unicode string to human-readable form
            try:
                repr_value = repr_value.decode('raw_unicode_escape').encode('utf-8')
            except UnicodeError:
                pass
            print >> self.stdout, repr_value
        except:
            pass
