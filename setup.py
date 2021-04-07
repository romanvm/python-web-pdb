# coding: utf-8
# Created on: 
# Author: Roman Miroshnychenko aka Roman V.M. (roman1972@gmail.com)
#
# Copyright (c) 2016 Roman Miroshnychenko
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import os
import re
from io import open
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

cwd = os.path.dirname(os.path.abspath(__file__))


def get_version():
    with open(os.path.join(cwd, 'web_pdb', '__init__.py')) as fo:
        return re.search(r'__version__ = \'(\d+\.\d+\.\d+)\'', fo.read()).group(1)


def get_doc(filename):
    with open(filename, encoding='utf-8') as fo:
        return fo.read()


setup(
    name='web-pdb',
    version=get_version(),
    author='Roman Miroshnychenko',
    author_email='roman1972@gmail.com',
    description='Web interface for Python\'s built-in PDB debugger',
    long_description=get_doc('Readme.rst') + u'\n\n' + get_doc('Changelog.rst'),
    url='https://github.com/romanvm/python-web-pdb',
    license='MIT License',
    packages=['web_pdb'],
    include_package_data=True,
    keywords='pdb remote web debugger',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Bottle',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Debuggers',
    ],
    install_requires=['bottle==0.12.19', 'asyncore-wsgi>=0.0.4'],
    test_suite='tests.tests',
    tests_require=['selenium==3.141.0'],
    platforms=['any'],
    zip_safe=False,
)
