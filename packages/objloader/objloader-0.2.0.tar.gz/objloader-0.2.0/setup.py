import os

from setuptools import setup

setup(
    name='objloader',
    version='0.2.0',
    description='ModernGL extension for loading obj files',
    url='https://github.com/cprogrammer1994/objloader',
    author='Szabolcs Dombi',
    author_email='cprogrammer1994@gmail.com',
    license='MIT',
    install_requires=['ModernGL', 'numpy'],
    packages=['objloader'],
    platforms=['any']
)
