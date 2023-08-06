=====
Usage
=====

This project delivers a script, ``smap``. This is my first project in python, so feel free to point out ways to improve it.

The sub-commands ``update`` and ``new`` expect a list of symbols given in stdin. The list of symbols are words separated by non-alphanumeric characters (matches with the regular expression ``[a-zA-Z0-9_]+``). For example::

  symbol, another, one_more

and::

  symbol
  another
  one_more

are valid inputs.

The last sub-command, ``check``, expects only the path to the map file to be
checked.

tl;dr
-----
::

  $ smap update lib_example.map < symbols_list

or (setting an output)::

  $ smap update lib_example.map -o new.map < symbols_list

or::

  $ cat symbols_list | smap update lib_example.map -o new.map

or (to create a new map)::

  $ cat symbols_list | smap new -r lib_example_1_0_0 -o new.map

or (to check the content of a existing map)::

  $ smap check my.map

Long version
------------

.. include:: ../HELP

Call a subcommand passing '-h' to see its specific options
There are three subcommands, ``update``, ``new``, and ``check``

.. include:: ../HELP_UPDATE

.. include:: ../HELP_NEW

.. include:: ../HELP_CHECK

Import as a library:
--------------------

To use smap in a project as a library::

	from smap import symver
