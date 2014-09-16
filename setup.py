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
        'devassistant==0.10.0.dev2',
        'PyYAML',
        'python-social-auth>=0.2',
        'django-taggit',
        'django-simple-captcha',
        'django-haystack',
        'whoosh',
        'djangorestframework>=2.4',
        'django-gravatar2',
        'markdown2',
        'Markdown',
    ],
    dependency_links = [
        'git+git://github.com/devassistant/devassistant.git@565a3cf#egg=devassistant-0.10.0.dev2',
    ]
)
