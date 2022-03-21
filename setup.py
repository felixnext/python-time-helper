import os
from setuptools import setup
from setuptools import find_packages


__status__      = "Package"
__copyright__   = "Copyright 2022"
__license__     = "MIT License"
__version__     = "0.1.0"

# 01101100 00110000 00110000 01110000
__author__      = "Felix Geilert"


this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'readme.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='time-helper',
    version=__version__,
    description='Various Helper Tools to handle different time data',
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords='time handling',
    url='https://github.com/felixnext/python-time-helper',
    author='Felix Geilert',
    license='MIT License',
    packages=find_packages(include=['time_helper', 'time_helper.*']),
    install_requires=['numpy', 'pandas', 'pytz'],
    setup_requires=['pytest-runner', 'flake8'],
    tests_require=['pytest'],
    include_package_data=True,
    zip_safe=False
)
