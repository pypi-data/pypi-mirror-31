# -*- coding=utf-8 -*-

from distutils.core import setup

setup(
    name = 'lgqhammer',
    version = '0.5.2',

    requires = ['pymysql'],

    packages = ['hammer'],
    scripts = ['./kill_port'],

    url = 'http://awolfly9.com/',
    license = 'MIT Licence',
    author = 'lgq',
    author_email = 'awolfly9@gmail.com',

    description = 'lgq hammer',
)
