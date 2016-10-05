#!/usr/bin/env python
# -*- coding: utf-8 -*-
import flask
import yaml

from hitsl_utils.api import api_method, ApiException
from hitsl_utils.safe import safe_traverse
from tsukino_usagi.loader import ConfigLoader
from tsukino_usagi.systemwide import app, cache

__author__ = "viruzzz-kun"
__version__ = "0.1"
__copyright__ = "Bars Group"


@app.route('/')
@api_method
def hello_world():
    return load_config()['subsystems']


@app.route('/favicon.ico')
def favicon():
    return flask.abort(404)


@app.route('/<subsys>')
# @app.route('/<subsys>/')
@api_method
def get_config(subsys):
    try:
        config = load_config()['subsystems'][subsys]
    except KeyError:
        raise ApiException(404, 'Subsystem "%s" not found' % subsys)
    return config['app']


def load_config_int():
    import os
    filename = os.getenv('TSUKINO_USAGI_CONFIG')
    if not filename:
        raise Exception(u'TSUKINO_USAGI_CONFIG must be set and point to actual YAML configuration')
    try:
        with open(filename, 'r') as fin:
            return yaml.load(fin, ConfigLoader)
    except (OSError,):
        raise  # Exception(u'"%s" not found' % filename)
    except (yaml.YAMLError,):
        raise


def init_app_config():
    cnf = load_config_int()
    app.config.update(safe_traverse(cnf, 'subsystems', 'tsukino_usagi', 'app'))


init_app_config()


cache.init_app(app)
load_config = cache.cached(timeout=60, key_prefix='internals/%s')(load_config_int)


if __name__ == '__main__':
    app.run(port=6702)

