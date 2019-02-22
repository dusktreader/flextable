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
* poetry
* postgres

Setup
-----

The project uses `poetry <https://poetry.eustace.io/>`_ to install the
application and to manage dependencies. Poetry also creates/activates a virtual
environment for the application so the user need not concern themselves with
managing virtual environments

Install the flextable package for development
.......................................

In order to install the flextable package for development and to include all
its dependencies, execute this command::

$ poetry install --dev

Running tests
=============

Using a local testing database
..............................

TODO
In order to run the tests, you will need a test database set up. This can
be on your local machine or on a remote system you can access.

By default the URI for the test database is::

   postgresql+psycopg2://postgres@localhost:5432/flextable_test

If you wish to override this and target a different database, you simply need
to set TEST_DATABASE_URI in your environment

Invokation
----------

This project uses `pytest <http://doc.pytest.org/en/latest/>`_

Tests can be executed like so::

$ poetry run pytest tests

Code Formatting
===============

Code formatting is enforced by `black <https://github.com/ambv/blacka>`_ with
a git pre-commit hook.

If you wish to run the black style-checker and code-formatter directly, you
can invoke it as::

$ poetry run black flextable
