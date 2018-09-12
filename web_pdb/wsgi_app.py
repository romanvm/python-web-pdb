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

import gzip
import json
import os
from functools import wraps
from io import BytesIO
from shutil import copyfileobj
import bottle

__all__ = ['app']

# bottle.debug(True)

cwd = os.path.dirname(os.path.abspath(__file__))
bottle.TEMPLATE_PATH.append(os.path.join(cwd, 'templates'))
static_path = os.path.join(cwd, 'static')
try:
    string_type = basestring
except NameError:
    string_type = (bytes, str)
    unicode = str


def compress(route):
    """
    Compress route return data with gzip compression
    """
    @wraps(route)
    def wrapper(*args, **kwargs):
        response = route(*args, **kwargs)
        if 'gzip' in bottle.request.headers.get('Accept-Encoding', ''):
            fo = BytesIO()
            if isinstance(response, string_type):
                if isinstance(response, unicode):
                    response = response.encode('utf-8')
                with gzip.GzipFile(mode='wb', fileobj=fo) as gzip_fo:
                    gzip_fo.write(response)
                # gzip_fo must be closed, otherwise getvalue returns truncated data
                response = fo.getvalue()
                bottle.response.add_header('Content-Encoding', 'gzip')
            elif hasattr(response, 'body') and hasattr(response.body, 'close'):
                with gzip.GzipFile(mode='wb', fileobj=fo) as gzip_fo:
                    copyfileobj(response.body, gzip_fo)
                response.body = fo
                fo.seek(0, 2)
                response.headers['Content-Length'] = str(fo.tell())
                fo.seek(0)
                response.add_header('Content-Encoding', 'gzip')
        return response
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
@compress
def get_static(path):
    return bottle.static_file(path, root=static_path)
