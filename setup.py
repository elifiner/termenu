#!/usr/bin/env python
# Copyright (C) 2011 Eli Finer <eli.finer@gmail.com>.
#
# This file is part of termenu.
#
# termenu is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3, or (at your option) any later
# version.
#
# termenu is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU General Public License
# along with termenu.  If not, see <http://www.gnu.org/licenses/>.

from distutils.core import setup
from termenu.version import version

DESCRIPTION = """
Termenu is a command line utility and Python library for displaying console
based interactive menus.

Traditionally there are two types of applications running the Unix shell: pure
command line utilities such as grep, sed and awk and full screen interactive
applications such as Midnight Commander. Termenu aims to bridge this gap and
allow a modicum of interactivity in regular command line utilities.
"""

setup(
    name='termenu',
    version=version,
    description='Interactive in-line menus for Unix-based terminals',
    long_description=DESCRIPTION,
    author='Eli Finer',
    license='GPL',
    author_email='eli.finer@gmail.com',
    url='https://github.com/elifiner/termenu',
    packages=['termenu'],
    scripts=['scripts/termenu'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Terminals'
    ]
)
