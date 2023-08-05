*********************************************
lazr.postgresql: Launchpad PostgreSQL support
*********************************************

    Copyright (c) 2011-2018, Canonical Ltd

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, version 3 only.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program.  If not, see <http://www.gnu.org/licenses/>.
    GNU General Public License version 3 (see the file LICENSE).

lazr.postgresql contains various helpers used by Launchpad for PostgreSQL
support. Primary amongst these is the Slony aware database migrations facility.

Dependencies
============

* Python 2.7+

Testing Dependencies
====================

* subunit (http://pypi.python.org/pypi/python-subunit) (optional)

* testtools (http://pypi.python.org/pypi/testtools)

* van.pg (http://pypi.python.org/pypi/van.pg)

Usage
=====

Database migrations
+++++++++++++++++++

The upgrade tool will apply data migrations to PostgreSQL or Slony
environments.

Each migration is a SQL file named patch-$major-$minor-$point-$type.sql.
Major, minor and point are integers that provide a sequence for how patches
are applied.
The type tells the migration applier whether the migration should be applied
in a normal transaction, directly to all the nodes in the cluster in a
transaction, or directly to all the nodes in a cluster outside of a transaction.
These are indicated by 'std', 'direct' and 'concurrent'.

If a patch application is interrupted in anything other than 'standard' mode,
manual cleanup may be required (e.g. because a half built index will be in
place on some nodes).

For instance a file called patch-1-2-3-concurrent.sql will be applied in the
following way on a non-Slony environment:

* A transaction on the master will be opened and the row 1-2-3 added to the list
  of applied patches. This prevents other migrations being attempted
  simultaneously.
* Then the contents of the patch file will be executed.
* The end timestamp for the 1-2-3 row will be updated.
* Finally the transaction is committed.

In a Slony environment the following would happen:

* A transaction on the master will be opened and the row 1-2-3 added to the list
  of applied patches. This prevents other migrations being attempted
  simultaneously.
* On all nodes the the contents of the patch file will be executed in separate
  connections outside of a transaction.
* The end timestamp for the 1-2-3 row will be updated.
* Finally the transaction is committed.

A single invocation of upgrade.py will only apply std, or direct + concurrent
patches unless the --all parameter is given, when it will loop until all
patches are applied.

More coming soon.

Installation
============

Either run setup.py in an environment with all the dependencies available, or
add the working directory to your PYTHONPATH.

Development
===========

Upstream development takes place at https://launchpad.net/lazr-postgresql.
To setup a working area for development, if the dependencies are not
immediately available, you can use ./bootstrap.py to create bin/buildout, then
bin/py to get a python interpreter with the dependencies available.

To run the tests use the runner of your choice, the test suite is
lazr.postgresql.tests.test_suite.

For instance::

  $ PYTHONPATH=src bin/py -m testtools.run lazr.postgresql.tests.test_suite

If you have testrepository you can run the tests with it:

  $ testr run


