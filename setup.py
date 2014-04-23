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
        'python-social-auth==c5dd3339',
        'django-taggit',
        'django-simple-captcha',
        'django-haystack',
        'whoosh',
        'djangorestframework==03b4c60b',
        'django-gravatar2',
        'markdown2',
    ],
    dependency_links = [
        'git+git://github.com/omab/python-social-auth.git@c5dd3339#egg=python-social-auth-c5dd3339',
        'git+git://github.com/tomchristie/django-rest-framework.git@03b4c60b#egg=djangorestframework-03b4c60b',
    ]
)
