# coding: utf-8
# Author: Roman Miroshnychenko aka Roman V.M.
# E-mail: romanvm@yandex.ua

from __future__ import absolute_import

import os
import bottle

__all__ = ['app']

bottle.debug(True)

cwd = os.path.dirname(os.path.abspath(__file__))
bottle.TEMPLATE_PATH.append(os.path.join(cwd, 'templates'))
static_path = os.path.join(cwd, 'static')


class WebConsoleApp(bottle.Bottle):
    def __init__(self):
        super(WebConsoleApp, self).__init__()
        self.in_queue = None
        self.history = None


app = WebConsoleApp()


@app.route('/')
def root():
    return bottle.template('index')


@app.route('/output/<mode>')
def send(mode):
    bottle.response.content_type = 'text/plain'
    bottle.response.cache_control = 'no-cache'
    if mode == 'history' or app.history.is_dirty:
        return app.history.get()
    else:
        raise bottle.HTTPError(403, 'Forbidden')


@app.route('/input', method='POST')
def receive():
    app.in_queue.put(bottle.request.body.read().decode('utf-8'))
    return ''


@app.route('/static/<path:path>')
def get_static(path):
    return bottle.static_file(path, root=static_path)
