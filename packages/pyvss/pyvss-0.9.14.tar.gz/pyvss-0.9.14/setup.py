#!/usr/bin/env python
import pyvss
import os
import io

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def required():
    with io.open('requirements.txt', encoding='utf-8') as f:
        return f.read().splitlines()


def read(fname):
    with io.open(os.path.join(os.path.dirname(__file__), fname),
                 encoding='utf-8') as fo:
        return fo.read()


setup(name='pyvss',
      version=pyvss.__version__,
      description='Python client to the ITS Private Cloud API',
      long_description=read('README.rst'),
      author='University of Toronto - ITS',
      author_email='jm.lopez@utoronto.ca',
      maintainer='JM Lopez',
      maintainer_email='jm.lopez@utoronto.ca',
      url='https://gitlab-ee.eis.utoronto.ca/vss/py-vss',
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Developers',
                   'Operating System :: OS Independent',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3.6',
                   'Topic :: Software Development :: Libraries :: Python Modules'],
      license='MIT License',
      packages=['pyvss'],
      download_url='https://gitlab-ee.eis.utoronto.ca/vss/py-vss',
      platforms=['Windows', 'Linux', 'Solaris', 'Mac OS-X', 'Unix', 'OpenBSD'],
      install_requires=required()
      )
