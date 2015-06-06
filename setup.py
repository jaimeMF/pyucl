# encoding: utf-8
from setuptools import setup

cffi_require = 'cffi>=1.0.0'
setup(
    name='pyucl',
    version='0.0',
    description='Wrapper for the libucl library',
    author='Jaime Marquínez Ferrándiz',
    author_email='jaime.marquinez.ferrandiz@gmail.com',
    py_modules=['ucl'],
    setup_requires=[cffi_require],
    cffi_modules=['ucl_build.py:ffi'],
    install_requires=[
        cffi_require,
    ],
    zip_safe=False,
)
