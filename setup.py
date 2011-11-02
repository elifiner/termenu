#!/usr/bin/env python
# Copyright (C) 2011 Eli Golovinsky <eli.golovinsky@gmail.com>.
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

DESCRIPTION = """
Shows an inline interactive menu. Menu items can be supplied as arguments,
via STDIN (if no arguments were given) or a file (using -f).
Menus can be vertical (multi-line) or one-line.
"""

setup(
    name='termenu',
    version='0.1.1',
    description='Interactive in-line menus for Unix-based terminals',
    long_description=DESCRIPTION,
    author='Eli GOlovinsky',
    license='GPL',
    author_email='eli.golovinsky@gmail.com',
    url='https://github.com/gooli/termenu',
    packages=['termenu'],
    scripts=['termenu/termenu'],
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

