# pg_materialize [![Travis Status](https://travis-ci.org/aanari/pg-materialize.svg?branch=master)](//travis-ci.org/aanari/pg-materialize) [![AppVeyor Status](https://ci.appveyor.com/api/projects/status/xfuqfl2pv1728c6x?svg=true)](https://ci.appveyor.com/project/aanari/pg-materialize/branch/master)
![pg_materialize](logo.jpg)

## Description

`pg_materialize` is a utility for generating PostgreSQL creation and refresh scripts from a directory containing [Materialized View](https://www.postgresql.org/docs/9.6/static/rules-materializedviews.html) SQL definitions. It uses [psqlparse](https://github.com/alculquicondor/psqlparse) to transform the SQL into parse trees, identifies which Materialized Views have a dependency on other views by generating a DAG, and produces the correct order for constructing and refreshing these views. The source directory is traversed recursively, cross-schema views are handled correctly, and extraneous transaction syntax blocks are filtered out from the final output. The files from each subsequent run are timestamped with the suffix `YYYYMMDD-HHMMSS.sql`.

## Supported Python Versions

- Python 2.6, 2.7
- Python 3.3+

## Installing

If you have [pip](https://pip.pypa.io/) on your system, you can simply install or upgrade the Python library:

```sh
pip install -U pg_materialize
```

Alternately, you can download the source distribution from [PyPI](http://pypi.python.org/pypi/pg-materialize), unarchive it, and run:

```sh
python setup.py install
```

Note: both of the methods described above install `pg_materialize` as a system-wide package. You may consider using [virtualenv](http://www.virtualenv.org/) to create isolated Python environments instead.

## Usage

**Example Command:**

```sh
pg_materialize -v \
    -i ~/Projects/my_project/src \
    -o ~/Projects/my_project/output \
    -p _mv \
    -I invites
```

**Example Output:**

```sh
Found 97 Scripts in /Users/ali/Projects/my_project/src
Identified 169 Materialized Views, Containing 90 View Dependencies

Materialized View Dependencies:
'public.users_mv': ['public.user_addresses_mv',
                    'public.user_invites_mv'],
'public.orders_mv': ['public.payment_methods_mv']

Selecting 97 Materialized Views for Refresh
Successfully Saved Creation Script to ~/Projects/my_project/output/create-20170824-120626.sql
Successfully Saved Refresh Script to ~/Projects/my_project/output/refresh-20170824-120626.sql
Process Complete!
```

**Example Creation Script:**

```sql
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
```

**Example Refresh Script:**

```sql
BEGIN;

    REFRESH MATERIALIZED VIEW CONCURRENTLY public.user_addresses_mv;
    
    REFRESH MATERIALIZED VIEW CONCURRENTLY public.payment_methods_mv;
    
    REFRESH MATERIALIZED VIEW CONCURRENTLY public.users_mv;
    
    REFRESH MATERIALIZED VIEW CONCURRENTLY public.orders_mv;

COMMIT;
```

## Options

`pg_materialize` accepts the following command line arguments.

`-d`  
`--dry-run`

- Analyzes dependencies without actually generating the output files.

`-i`  
`--input-dir`

- The directory for the PostgreSQL scripts to analyze.

`-I`  
`--ignore-refresh`

- Regex pattern to match when ignoring refresh on Materialized Views (i.e. "hist" for "users_mv_hist").

`-o`  
`--output_dir`

- The directory for the output creation and refresh scripts.

`-p`  
`--pattern`

- Materialized View regex pattern to match (i.e. "_mv" for "users_mv"),

`-v`  
`--verbose`

- Enables verbose logging.

## License (MIT)

Copyright (c) 2017 Ali Anari

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
