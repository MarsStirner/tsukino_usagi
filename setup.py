# -*- coding: utf-8 -*-
from setuptools import setup

__author__ = 'viruzzz-kun'
__version__ = '0.1'


if __name__ == '__main__':
    setup(
        name="tsukino-usagi",
        version=__version__,
        description="Central Configuration Service",
        long_description='',
        author=__author__,
        author_email="viruzzz.soft@gmail.com",
        license='ISC',
        url="https://stash.bars-open.ru/scm/medvtr/tsukino_usagi",
        packages=["tsukino_usagi"],
        zip_safe=False,
        install_requires=[
            'Flask',
            'PyYaml',
            'simplejson',
            'hitsl.utils',
        ],
        classifiers=[
            "Development Status :: 4 - Beta",
            "Environment :: No Input/Output (Daemon)",
            "Programming Language :: Python",
        ])
