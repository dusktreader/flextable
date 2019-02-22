***********
 FlexTable
***********

.. contents:: Table of Contents
   :local:
   :depth: 2


Developer Quick Start
=====================

Dependencies
------------

* python3
* pipenv

Setup
-----

NOTE
....

The project uses `pipenv <https://docs.pipenv.org>` to install the application
and to manage dependencies. Pipenv also creates/activates a virtual environment
for the application so the user need not concern themselves with managing
virtual environments

Install the flextable package for development
.......................................

In order to install the flextable package for development and to include all
its dependencies, execute this command::

$ pipenv install --dev

The full list of dependencies can be found in ``Pipfile``

Running tests
=============

Using a local testing database
..............................

TODO

Using a specific testing database
.................................

Invokation
----------

This project uses `pytest <http://doc.pytest.org/en/latest/>`_

Tests can be executed by invoking the ``tests`` helper script::

$ pipenv run tests

This command will run all the tests in random order and stop on the first
failure. There are also additional test helpers::

  $ pipenv run tests-verbose
  same as tests, but produce verbose output

  $ pipenv run tests-all
  do not stop on test failures

  $ pipenv run tests-coverage
  run all the tests, and produce a test coverage report (slower)

  $ pipenv run tests-watch
  see below

  $ pipenv run test <test_target>
  see below

Using pytest-testmon and pytest-watch
-------------------------------------

You can use the pytest-testmon and pytest-watch extensions to have pytest
watch for changes in your source and tests and run only the impacted tests
when the changes occur. This can be useful for having your tests being watched
in another terminal while you hack on a test or a module with existing tests.
Both of these extensions should install with the 'dev' optional dependencies.
to run a watcher, use the ``tests-watch`` helper script::

$ pipenv run tests-watch

See `pytest-testmon's github <https://github.com/tarpas/pytest-testmon>`_ for
more information
