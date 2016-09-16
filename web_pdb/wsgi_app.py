# coding: utf-8
# Author: Roman Miroshnychenko aka Roman V.M.
# E-mail: romanvm@yandex.ua
"""
Web-UI WSGI application
"""

import json
import os
import bottle

__all__ = ['app']

cwd = os.path.dirname(os.path.abspath(__file__))
bottle.TEMPLATE_PATH.append(os.path.join(cwd, 'templates'))
static_path = os.path.join(cwd, 'static')


class WebConsoleApp(bottle.Bottle):
    def __init__(self):
        super(WebConsoleApp, self).__init__()
        self.in_queue = None
        self.history = None
        self.variables = None
        self.frame_data = None


app = WebConsoleApp()


@app.route('/')
def root():
    return bottle.template('index')


@app.route('/output/<mode>')
def send(mode):
    if app.history.is_dirty or mode == 'history':
        bottle.response.content_type = 'application/json'
        bottle.response.cache_control = 'no-cache'
        return json.dumps({
            'history': app.history.contents,
            'variables': app.variables.contents,
            'frame_data': app.frame_data.contents
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
