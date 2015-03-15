# encoding: utf-8
from setuptools import setup

setup(
    name='pyucl',
    version='0.0',
    description='Wrapper for the libucl library',
    author='Jaime Marquínez Ferrándiz',
    author_email='jaime.marquinez.ferrandiz@gmail.com',
    py_modules=['ucl'],
    install_requires=[
        'cffi>=0.9',
    ],
    zip_safe=False,
)
