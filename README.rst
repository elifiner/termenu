Abstract
========

Termenu is a command line utility and Python library for displaying console
based interactive menus.

Description
===========

Traditionally there are two types of applications running the Unix shell: pure
command line utilities such as grep, sed and awk and full screen interactive
applications such as Midnight Commander. Termenu aims to bridge this gap and
allow a modicum of interactivity in regular command line utilities. A common
example is finding and editing a file located somewhere in the directory tree.

The usual way to do this is to run::

  $ find . -name "*.py"

This will shown a list of files in the current directory and its
sub-directories::

  ./lib/keyboard.py
  ./lib/ansi.py
  ./termenu.py

Now you need to write a command to start the editor, using the mouse (gasp!) to
copy and paste the required filename to the command line, like so::

  $ vim ./lib/keyboard

In its simplest use-case, termenu allows you to choose one or more of the lines
you pass to it in an interactive way. The following command will allow you to
choose one or more of the files returned by the ``find`` command::

  $ find . -name "*.py" | termenu

A simple modification will start the ``vim`` editor with the selected files::

  $ vim `find . -name "*.py" | termenu`

Usage
=====
::

  termenu [items] [options]

  --help                Show help message
  -f FILE, --file=FILE  Take menu items from a file
  -d OPTION, --default=OPTION
                        Default item to select
  -h N, --height=N      Max height [10]
  -o, --one             Don't show a menu if only one option was given
  -p, --precolored      Preserve ANSI coloring in supplied options
  -i, --inline          Show small inline menu on a sinel line
  --single              Single selection only

Examples
========

Show the contents of a recent commit in ``git``::

  $ git show `git log --oneline --color | termenu -p | awk '{print $1}'`

Ask a multiple choice question::

  $ echo -n "Would you like to exit? " && ./termenu -i Yes No Maybe

See Also
========

If you like termenu, you may find `gitter <http://github.com/gooli/gitter>`_
interesting as well. It's a termenu based git client that acts exactly like the
standard command line git but shows a menu whenver appropriate. It's similar to
how git works under zsh, but works with standard shells and has smarter menus.

Name
====

Oh, and if you were wondering, termenu is a combination of the words *terminal* and *menu*.

Version History
===============

1.1.4
-----

* fixed a rare ansi sequence parsing issue when holding down a key

1.1.3
-----

* fixed a rare 'Resource temporarily unavailable' bug

1.1.2
-----

* Minor visual improvements to showing ANSI-colored menu items

1.1.1
-----

* fixed 'Resource temporarily unavailable' bug
* reduced flickering and amount of screen updates

1.1.0
-----

* added simple show_menu function as a frontend for simple use in Python scripts
* added support for time-based updates and added example of a slow loading menu
* python 3k compatibility (by bladmorv)
* many small bug fixes

1.0.2
-----

* added width restriction for the menu (including support for
  ANSI menu items)

1.0.1
-----

* added support for a static title above the menu
* added some complex examples (filemenu and longmeny)

1.0.0
-----

* completely reimplemented based on plugins
* includes support for multi-selection and filtering
* removed multi-column support
* added simple one line minimenu
* added comprehensive unit tests
* added support for ANSI colored menu items
* added support multiple headers

0.3.0
-----

* first public version
