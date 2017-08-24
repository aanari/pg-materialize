pg_materialize [![Travis Status](https://travis-ci.org/aanari/pg-materialize.svg?branch=master)](//travis-ci.org/aanari/pg-materialize) [![AppVeyor Status](https://ci.appveyor.com/api/projects/status/xfuqfl2pv1728c6x?svg=true)](https://ci.appveyor.com/project/aanari/pg-materialize/branch/master)
========
![pg_materialize](logo.jpg)

## Description

`pg_materialize` is a utility for generating PostgreSQL creation and refresh scripts from a folder of [Materialized View](https://www.postgresql.org/docs/9.6/static/rules-materializedviews.html) SQL definitions. It uses [psqlparse](https://github.com/alculquicondor/psqlparse) to transform the SQL into parse trees, identifies which Materialized Views have a dependency on other views by generating a DAG, and produces the correct order for constructing and refreshing these views. Cross-schema views are handled correctly, and extraneous transaction blocks are filtered out from the final output. The files from each subsequent run are timestamped with the suffix `YYYYMMDD-HHMMSS.sql`.

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

## Example

**Command:**

```sh
pg_materialize -v \
    -i ~/Projects/my_project/src \
    -I hist \
    -o ~/Projects/my_project/output
```

**Output:**

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
```
