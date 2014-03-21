#!/usr/bin/env python

from setuptools import setup

setup(
    name='Dapi',
    version='1.0',
    description='DevAssistant Package Index',
    author='Miro Hroncok',
    author_email='mhroncok@redhat.com',
    url='http://www.python.org/sigs/distutils-sig/',
    install_requires=['Django<=1.4','psycopg2'],
)
