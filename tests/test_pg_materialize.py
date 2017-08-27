import unittest
import pg_materialize.pg_materialize as pgm


class PgMaterializeTest(unittest.TestCase):

    def test_extract_nodes(self):

        query = """
            BEGIN;

              CREATE MATERIALIZED VIEW IF NOT EXISTS schema1.messages_mv
              AS (
                SELECT
                  DATE(e.created_on) AS creation_date,
                  m.account_id
                FROM schema1.events_mv e
                INNER JOIN schema2.members_mv m
                  ON e.member_id = m.id
                LEFT JOIN schema3.log_mv l
                  ON l.event_id = e.id
                WHERE e.event_type = 'TEST'
                GROUP BY creation_date, m.account_id
                ORDER BY 1, 2 ASC
              ) WITH DATA;

            COMMIT;
        """
    
        actual = pgm.extract_nodes(query, '_mv')
        expected = {
            'dependencies': set(['schema3.log_mv', 'schema1.events_mv', 'schema2.members_mv']),
            'views': set(['schema1.messages_mv'])
        }
        self.assertEqual(actual, expected)

        query = """
            CREATE MATERIALIZED VIEW schema1.messages_mv
              AS (
                SELECT
                  DATE(e.created_on) AS creation_date,
                  m.account_id
                FROM (
                  SELECT *
                  FROM schema1.events
                ) e
                INNER JOIN schema2.members m
                  ON e.member_id = m.id
                LEFT JOIN schema3.log_mv l
                  ON l.event_id = e.id
                WHERE e.event_type = 'TEST'
                GROUP BY creation_date, m.account_id
                ORDER BY 1, 2 ASC
              )
        """

        actual = pgm.extract_nodes(query, '_mv')
        expected = {
            'dependencies': set(['schema3.log_mv']),
            'views': set(['schema1.messages_mv'])
        }
        self.assertEqual(actual, expected)


    def test_format_content(self):

        entity = {
            'file_name': 'src/members.sql',
            'content': """
BEGIN;

  CREATE MATERIALIZED VIEW public.members_mv
    AS (
      SELECT * FROM public.members LIMIT 1000;
    );

COMMIT;
            """
        }

        actual = pgm.format_content(entity)
        expected = """
  -- src/members.sql


  CREATE MATERIALIZED VIEW public.members_mv
    AS (
      SELECT * FROM public.members LIMIT 1000;
    );
        """

        self.assertEqual(actual.strip(), expected.strip())


    def test_generate_script(self):

        views = ['  DEFINE_VIEW_1;', '  DEFINE_VIEW_2;', '  DEFINE_VIEW_3;']
        actual = pgm.generate_script(views, "\n")
        expected = """
BEGIN;

  DEFINE_VIEW_1;
  DEFINE_VIEW_2;
  DEFINE_VIEW_3;

COMMIT;
        """

        self.assertEqual(actual.strip(), expected.strip())


    def test_process_file(self):

        expected = pgm.process_file('tests/fixtures/members.sql', '_mv')['views']
        actual = set(['my_schema.members_mv'])
        self.assertEqual(actual, expected)

        with self.assertRaises(Exception):
          pgm.process_file('tests/fixtures/invalid.sql', '_mv')


    def test_walk_directory_recursively(self):
        expected = set(pgm.walk_directory_recursively('tests/fixtures'))
        actual = set(['tests/fixtures/invalid.sql', 'tests/fixtures/members.sql'])
        self.assertEqual(actual, expected)
