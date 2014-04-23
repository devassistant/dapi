#!/usr/bin/env python

from setuptools import setup

setup(
    name='Dapi',
    version='1.0',
    description='DevAssistant Package Index',
    author='Miro Hroncok',
    author_email='mhroncok@redhat.com',
    url='https://github.com/hroncok/dapi',
    license='AGPLv3',
    install_requires=[
        'Django==1.6',
        'psycopg2',
        'South',
        'daploader>=0.0.4',
        'PyYAML',
        'python-social-auth',
        'django-taggit',
        'django-simple-captcha',
        'django-haystack',
        'whoosh',
        'djangorestframework==03b4c60b',
        'django-gravatar2',
    ],
    dependency_links = [
        'git+git://github.com/tomchristie/django-rest-framework.git@03b4c60b#egg=djangorestframework-03b4c60b',
    ]
)
