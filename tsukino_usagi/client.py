# -*- coding: utf-8 -*-
import requests
import logging

import time

import yaml

from tsukino_usagi.loader import ConfigLoader

__author__ = 'viruzzz-kun'


handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s [pid:%(process)d|%(name)s|%(levelname)s] - %(message)s'))
logger = logging.getLogger('Usagi')
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


class TsukinoUsagiClient(object):
    """
    Usage example:

    >>> import os
    ... from flask import Flask
    ... app = Flask(__name__)
    ... 
    ... class MyUsagi(TsukinoUsagiClient):
    ...     def on_configuration(self, configuration):
    ...         app.config.update(configuration)
    ...
    ... usagi = MyUsagi(
    ...     app.wsgi_app, 
    ...     os.getenv('TSUKINO_USAGI_URL'), 
    ...     os.getenv('TSUKINO_USAGI_SUBSYSTEM')
    ... )
    ... app.wsgi_app = usagi.app
    ... usagi()
    """

    def __init__(self, app, url, subsystem):
        self.wsgi_app = app
        self.url = url.rstrip('/')
        self.subsystem = subsystem
        self.configured = False

    def __call__(self, style='blocking'):
        if self.url.startswith('file://'):
            self.url = self.url[7:]
        if self.url.startswith('/'):
            style = 'file'
        method = getattr(self, 'trier_' + style)
        if method:
            method()
        else:
            logger.error('Style %s not implemented')
            raise NotImplemented

    def trier_file(self):
        with open(self.url, 'r') as f:
            yml = yaml.load(f, ConfigLoader)
        config = yml['subsystems'][self.subsystem]['app']
        logger.debug('Applying configuration from file')
        self.on_configuration(config)
        self.configured = True
        logger.debug('Application configured')

    def trier_blocking(self):
        self.trier()

    def trier_threading(self):
        import threading
        threading.Thread(target=self.trier).start()

    def trier_uwsgi(self):
        import uwsgidecorators
        uwsgidecorators.thread(self.trier)()

    def trier(self):
        url = '%s/%s' % (self.url, self.subsystem)
        logger.debug('Tsukino Usagi URL: %s', url)
        while 1:
            try:
                result = requests.get(url)
            except requests.ConnectionError:
                logger.error('Connection error')
                self.on_error()
                continue
            if result.status_code != 200:
                logger.error(result.content)
                self.on_error()
                continue
            try:
                config = result.json()['result']
            except ValueError:
                logger.error('Invalid JSON')
                self.on_error()
                continue
            logger.debug('Applying configuration')
            self.on_configuration(config)
            self.configured = True
            logger.debug('Application configured')
            return

    def on_configuration(self, configuration):
        """
        Called when got configuration
        :param configuration: config dictionary
        :return:
        """

    def on_error(self):
        """
        Called when error
        """
        time.sleep(10)

    def app(self, environ, start_response):
        if self.configured:
            return self.wsgi_app(environ, start_response)
        else:
            return self.__default_app(environ, start_response)

    @staticmethod
    def __default_app(environ, start_response):
        start_response('500 Not configured yet', [('content-type', 'text/plain')])
        yield 'Not configured yet'


