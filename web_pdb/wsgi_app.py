# coding: utf-8
# Author: Roman Miroshnychenko aka Roman V.M.
# E-mail: romanvm@yandex.ua
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
import bottle

__all__ = ['app']

# bottle.debug(True)

cwd = os.path.dirname(os.path.abspath(__file__))
bottle.TEMPLATE_PATH.append(os.path.join(cwd, 'templates'))
static_path = os.path.join(cwd, 'static')


class WebConsoleApp(bottle.Bottle):
    def __init__(self):
        super(WebConsoleApp, self).__init__()
        self.in_queue = None
        self.history = None
        self.globals = None
        self.locals = None
        self.frame_data = None


app = WebConsoleApp()


@app.route('/')
def root():
    return bottle.template('index')


@app.route('/output/<mode>')
def send(mode):
    if app.history.is_dirty or mode == 'history':
        bottle.response.content_type = 'application/json; charset=UTF-8'
        bottle.response.cache_control = 'no-cache'
        return json.dumps({
            'history': app.history.contents,
            'globals': app.globals.contents,
            'locals': app.locals.contents,
            'frame_data': app.frame_data.contents,
        })
    else:
        raise bottle.HTTPError(403, 'Forbidden')


@app.route('/input', method='POST')
def receive():
    app.in_queue.put(bottle.request.body.read().decode('utf-8'))
    return ''


@app.route('/static/<path:path>')
def get_static(path):
    return bottle.static_file(path, root=static_path)
