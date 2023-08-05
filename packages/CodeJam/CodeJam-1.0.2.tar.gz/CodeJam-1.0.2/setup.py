from io import open
from setuptools import setup

setup(
    name='CodeJam',
    version='1.0.2',
    author='Chris Knott',
    author_email='chrisknott@hotmail.co.uk',
    packages=['codejam'],
    install_requires=['networkx'],
    description='Convenience functions for Google Code Jam',
    long_description=open('README.txt').read(),
)