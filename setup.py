#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages

f = open('VERSION', 'r')
version = f.readline().strip()
f.close()

author = 'Jens Janssen'
author_email = 'janssen@physik.uni-bonn.de'

setup(
    name='CCPDv4',
    version=version,
    description='pyCPIX CCPDv4',
    url='https://github.com/SiLab-Bonn/ccpdv4',
    license='BSD 3-Clause ("BSD New" or "BSD Simplified") License',
    long_description='',
    author=author,
    maintainer=author,
    author_email=author_email,
    maintainer_email=author_email,
    install_requires=['pyBAR>=2.1.0dev', 'basil_daq==2.4.2'],
    packages=find_packages(),  # exclude=['*.tests', '*.test']),
    include_package_data=True,  # accept all data files and directories matched by MANIFEST.in or found in source control
    package_data={'': ['README.*', 'VERSION'], 'docs': ['*'], 'examples': ['*'], 'ccpdv4': ['*.yaml', '*.bit']},
    platforms='any'
)
