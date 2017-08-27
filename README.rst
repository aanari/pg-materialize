pg_materialize
==============

.. image:: https://badge.fury.io/py/pg-materialize.svg
  :target: https://badge.fury.io/py/pg-materialize

.. image:: https://travis-ci.org/aanari/pg-materialize.svg?branch=master
  :target: https://travis-ci.org/aanari/pg-materialize

.. image:: https://coveralls.io/repos/github/aanari/pg-materialize/badge.svg?branch=master
  :target: https://coveralls.io/github/aanari/pg-materialize?branch=master

.. figure:: logo.jpg

``pg_materialize`` is a utility for generating PostgreSQL creation and refresh scripts from a directory containing `Materialized View <https://www.postgresql.org/docs/9.6/static/rules-materializedviews.html>`_ SQL definitions. It uses `psqlparse <https://github.com/alculquicondor/psqlparse>`_ to transform the SQL into parse trees, identifies which Materialized Views have a dependency on other views by generating a DAG, and produces the correct order for constructing and refreshing these views. The source directory is traversed recursively, cross-schema views are handled correctly, and extraneous transaction syntax blocks are filtered out from the final output. The files from each subsequent run are timestamped with the suffix ``YYYYMMDD-HHMMSS.sql``.

Supported Python Versions
-------------------------

- Python 2.7
- Python 3.3+

Installation
------------

If you have `pip <https://pip.pypa.io/>`_ on your system, you can simply install or upgrade the Python library:

.. code:: sh

  pip install -U pg_materialize

Alternately, you can download the source distribution from `PyPI <http://pypi.python.org/pypi/pg-materialize>`_, unarchive it, and run:

.. code:: sh

  python setup.py install

Note: both of the methods described above install ``pg_materialize`` as a system-wide package. You may consider using `virtualenv <http://www.virtualenv.org/>`_ to create isolated Python environments instead.

Usage
-----

**Example Command:**

.. code:: sh

  pg_materialize -v \
      -i ~/Projects/my_project/src \
      -o ~/Projects/my_project/output \
      -p _mv \
      -I invites

**Example Output:**

.. parsed-literal::

  Found 97 Scripts in /Users/ali/Projects/my_project/src
  Identified 169 Materialized Views, Containing 90 View Dependencies
  
  Materialized View Dependencies:
  'public.users_mv': ['public.user_addresses_mv', 'public.user_invites_mv'],
  'public.orders_mv': ['public.payment_methods_mv']
  
  Selecting 97 Materialized Views for Refresh
  Successfully Saved Creation Script to ~/Projects/my_project/output/create-20170824-120626.sql
  Successfully Saved Refresh Script to ~/Projects/my_project/output/refresh-20170824-120626.sql
  Process Complete!

**Example Creation Script:**

.. code:: sql

  BEGIN;
  
      -- ~/Projects/my_project/src/public/user_addresses.sql
  
      CREATE MATERIALIZED VIEW IF NOT EXISTS public.user_addresses_mv AS (
          SELECT *
          FROM public.user_addresses
          WHERE created_at >= CURRENT_DATE - INTERVAL '6 MONTHS'
      ) WITH DATA;
  
      -- ~/Projects/my_project/src/public/user_invites.sql
  
      CREATE MATERIALIZED VIEW IF NOT EXISTS public.user_invites_mv AS (
          SELECT *
          FROM public.user_invites
          WHERE created_at >= CURRENT_DATE - INTERVAL '6 MONTHS'
      ) WITH DATA;
  
      -- ~/Projects/my_project/src/public/payment_methods.sql
  
      CREATE MATERIALIZED VIEW IF NOT EXISTS public.payment_methods_mv AS (
          SELECT *
          FROM public.payment_methods
          WHERE created_at >= CURRENT_DATE - INTERVAL '6 MONTHS'
      ) WITH DATA;
  
      -- ~/Projects/my_project/src/public/users.sql
  
      CREATE MATERIALIZED VIEW IF NOT EXISTS public.users_mv AS (
          SELECT *
          FROM public.users
          WHERE created_at >= CURRENT_DATE - INTERVAL '6 MONTHS'
      ) WITH DATA;
  
      -- ~/Projects/my_project/src/public/orders.sql
  
      CREATE MATERIALIZED VIEW IF NOT EXISTS public.orders_mv AS (
          SELECT *
          FROM public.orders
          WHERE created_at >= CURRENT_DATE - INTERVAL '6 MONTHS'
      ) WITH DATA;
  
  COMMIT;

**Example Refresh Script:**

.. code:: sql

  BEGIN;
  
      REFRESH MATERIALIZED VIEW CONCURRENTLY public.user_addresses_mv;
      
      REFRESH MATERIALIZED VIEW CONCURRENTLY public.payment_methods_mv;
      
      REFRESH MATERIALIZED VIEW CONCURRENTLY public.users_mv;
      
      REFRESH MATERIALIZED VIEW CONCURRENTLY public.orders_mv;
  
  COMMIT;

Options
-------

``pg_materialize`` accepts the following command line arguments.

| ``-d``
| ``--dry-run``

  Analyzes dependencies without actually generating the output files.

| ``-i``
| ``--input-dir``

  The directory for the PostgreSQL scripts to analyze.


| ``-I``
| ``--ignore-refresh``

  Regex pattern to match when ignoring refresh on Materialized Views (i.e. ``hist`` for ``users_mv_hist``).

| ``-o``
| ``--output_dir``

  The directory for the output creation and refresh scripts.


| ``-p``
| ``--pattern``

  Materialized View regex pattern to match (i.e. ``_mv`` for ``users_mv``).

| ``-v``
| ``--verbose``

  Enables verbose logging.
