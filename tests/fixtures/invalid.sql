BEGIN;

  CREATE MATERIALIZED VIEW IF NOT EXISTS my_schema.members_mv;
    AS (;
      SELECT *
      FROM my_schema.members;
    ) WITH DATA;

COMMIT;
