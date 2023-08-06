#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup
from dj_markdown import __version__

try:
    long_description = open('README.rst').read()
except:
    long_description = "Django Markdown custom plugin and template tags"

try:
    license = open('LICENSE.txt').read()
except:
    license = "MIT License"


REQUIREMENTS = [
    'mistune==0.8.3',
    'Pygments==2.2.0',
]
TEST_REQUIRED = [
    'flake8',
    'pytest',
]

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
]

setup(
    name='dj_markdown',
    version=__version__,
    description='Django Markdown custom plugin and template tags',
    author='Carlos Martínez',
    author_email='carlosmart626@gmail.com',
    url='https://github.com/CarlosMart626/dj_markdown',
    packages=find_packages(),
    package_data={'': ['README.md']},
    install_requires=REQUIREMENTS,
    license=license,
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    long_description=long_description,
    include_package_data=True,
    zip_safe=False,
    test_suite='tests.settings.run',
    keywords='django markdown templatetags code highlight',
)
