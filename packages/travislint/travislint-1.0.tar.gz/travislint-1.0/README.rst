====================
travislint |builds|
====================
Disclaimer: I have no connection to `travis-ci`_ at all other than being a satisfied customer.  I wrote this utility to avoid having to install Ruby, dependencies etc in order to run the `travis-ci`_ command line tool which does far more than I actually needed.

What It Does
------------
This is a Python utility that parses your `travis-ci`_ configuration file and lints whether it is valid generic YAML before passing it to `travis-ci`_'s own linter.

Installation
------------
It is recommended that you install the utility into either `Virtualenv`_ or `Venv`_ environment after which the following should install this utility:
::

  $ pip install travislint


The travislint application can then be run to lint your `travis-ci`_ configuration file.

Usage
-----
::

  travislint [-h] [-v] [filename]

  Lint a .travis.yml file

  positional arguments:
    filename       name of the file to lint (default: .travis.yml)

  optional arguments:
    -h, --help     show this help message and exit
    -v, --verbose  verbose output of progress


Under the Covers
----------------
It turns out that the `travis-ci`_ command line tool does not actually lint your file itself but hands off this task to a portion of the `travis-ci`_ website.  So it was simple to do this using the Python `requests`_ package and save you from having to install Ruby etc.

.. _travis-ci: https://travis-ci.org
.. _requests: http://docs.python-requests.org/en/master/
.. _Virtualenv: https://virtualenv.pypa.io/en/stable/
.. _Venv: https://docs.python.org/3/library/venv.html
.. |builds| image:: https://travis-ci.org/papadeltasierra/travislint.svg?branch=master
