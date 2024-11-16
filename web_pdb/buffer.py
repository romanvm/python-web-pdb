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

from threading import RLock

__all__ = ['ThreadSafeBuffer']


class ThreadSafeBuffer:
    """
    A buffer for data exchange between threads
    """
    def __init__(self, contents=None):
        self._lock = RLock()
        self._contents = contents
        self._is_dirty = contents is not None

    @property
    def is_dirty(self):
        """Indicates whether a buffer contains unread data"""
        with self._lock:
            return self._is_dirty

    @property
    def contents(self):
        """Get or set buffer contents"""
        with self._lock:
            self._is_dirty = False
            return self._contents

    @contents.setter
    def contents(self, value):
        with self._lock:
            self._contents = value
            self._is_dirty = True
