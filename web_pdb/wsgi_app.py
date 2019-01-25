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
"""
Web-UI WSGI application
"""

import json
import os
import gzip
from functools import wraps
from io import BytesIO
import bottle

__all__ = ['app']

# bottle.debug(True)

this_dir = os.path.dirname(os.path.abspath(__file__))
bottle.TEMPLATE_PATH.append(os.path.join(this_dir, 'templates'))
static_path = os.path.join(this_dir, 'static')
try:
    string_type = basestring
except NameError:
    string_type = (bytes, str)
    unicode = str


def compress(func):
    """
    Compress route return data with gzip compression
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if ('gzip' in bottle.request.headers.get('Accept-Encoding', '') and
                isinstance(result, string_type) and
                len(result) > 1024):
            if isinstance(result, unicode):
                result = result.encode('utf-8')
            tmp_fo = BytesIO()
            with gzip.GzipFile(mode='wb', fileobj=tmp_fo) as gzip_fo:
                gzip_fo.write(result)
            result = tmp_fo.getvalue()
            bottle.response.add_header('Content-Encoding', 'gzip')
        return result
    return wrapper


class WebConsoleApp(bottle.Bottle):
    def __init__(self):
        super(WebConsoleApp, self).__init__()
        self.frame_data = None


app = WebConsoleApp()


@app.route('/')
@compress
def root():
    return bottle.template('index')


@app.route('/frame-data')
@compress
def get_frame_data():
    bottle.response.cache_control = 'no-store'
    bottle.response.content_type = 'application/json'
    return json.dumps(app.frame_data.contents)


@app.route('/static/<path:path>')
def get_static(path):
    return bottle.static_file(path, root=static_path)
