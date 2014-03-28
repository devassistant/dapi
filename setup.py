#!/usr/bin/env python

from setuptools import setup

setup(
    name='Dapi',
    version='1.0',
    description='DevAssistant Package Index',
    author='Miro Hroncok',
    author_email='mhroncok@redhat.com',
    url='http://www.python.org/sigs/distutils-sig/',
    install_requires=['Django==1.6', 'psycopg2', 'South', 'daploader>=0.0.4', 'PyYAML', 'python-social-auth'],
)
