# -*- coding: utf-8 -*-
import requests
import logging

import time

__author__ = 'viruzzz-kun'


logger = logging.getLogger('Usagi')
logger.addHandler(logging.StreamHandler())
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

    def __call__(self, *args, **kwargs):
        self.trier()

    def trier(self):
        url = '%s/%s' % (self.url, self.subsystem)
        logger.debug('Tsukino Usagi URL: %s', url)
        while 1:
            try:
                result = requests.get(url)
            except requests.ConnectionError:
                logger.exception('Connection error')
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


def configure_usagi():
    try:
        import uwsgidecorators

        logger.debug('Using uWSGI')
        TsukinoUsagiClient.__call__ = uwsgidecorators.thread(TsukinoUsagiClient.trier)
    except ImportError:
        try:
            import threading

            def __call__(self):
                threading.Thread(target=self.trier).run()

            logger.debug('Using threading')
            TsukinoUsagiClient.__call__ = __call__
        except ImportError:
            logger.critical('Cannot run application')
            exit(-1)

configure_usagi()
del configure_usagi
