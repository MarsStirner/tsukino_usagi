# -*- coding: utf-8 -*-
from flask import Flask
from flask.ext.cache import Cache

__author__ = 'viruzzz-kun'


app = Flask(__name__)

cache = Cache()