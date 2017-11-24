import sys
from distutils.core import setup
from setuptools import find_packages


setup(
    name='interpals-api',
    version='1.0',
    packages=find_packages(),
    license=open('LICENSE.txt').read(),
    long_description=open('README.md').read(),
    data_files=[],
    install_requires=[
        'pyyaml',
        'requests',
        'beautifulsoup4',
    ],
)
