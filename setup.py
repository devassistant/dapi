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
        'psycopg2==2.5.1',
        'South==1.0',
        'devassistant==0.10.0.dev2',
        'PyYAML==3.11',
        'python-social-auth==0.2.1',
        'django-taggit==0.11.2',
        'django-simple-captcha==0.4.2',
        'django-haystack==2.1.0',
        'whoosh==2.6.0',
        'djangorestframework==2.4.2',
        'django-gravatar2==1.1.4',
        'markdown2==2.2.1',
        'Markdown==2.4 ',
    ],
    dependency_links = [
        'git+git://github.com/devassistant/devassistant.git@565a3cf#egg=devassistant-0.10.0.dev2',
    ]
)
