# coding: utf-8
# Created on: 
# Author: Roman Miroshnychenko aka Roman V.M. (romanvm@yandex.ua)

import os
import re
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

cwd = os.path.dirname(os.path.abspath(__file__))


def get_version():
    with open(os.path.join(cwd, 'web_pdb', '__init__.py')) as fo:
        return re.search(r'__version__ = \'(\d+\.\d+\.\d+)\'', fo.read()).group(1)


def get_long_descr():
    with open('Readme.rst') as fo:
        return fo.read()


setup(
    name='web-pdb',
    version=get_version(),
    author='Roman Miroshnychenko',
    author_email='romanvm@yandex.ua',
    description='Web interface for Python\'s built-in PDB debugger',
    long_description=get_long_descr(),
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
    install_requires=['bottle'],
    test_suite = 'nose.collector',
    tests_require=['nose', 'selenium'],
    platforms=['any'],
    zif_safe=False,
)
