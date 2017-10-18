from __future__ import print_function

import click
import os
import re
import time

from psqlparse import parse
from psqlparse import nodes
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import Terminal256Formatter
from pprint import pformat
from toolz.curried import pipe, map, filter, get
from toolz.itertoolz import count, unique
from toolz.dicttoolz import valmap, valfilter
from toposort import toposort, toposort_flatten


def pprint_color(obj):
    print(highlight(pformat(obj), PythonLexer(), Terminal256Formatter()))

def extract_nodes(content, pattern):
    class NS(object):
        pass
    ns = NS()
    ns.views = set()
    ns.dependencies = set()

    def inner(data, depth):
        if isinstance(data, dict):
            if 'relname' in data and 'schemaname' in data and re.search(pattern, data['relname']):
                entity = '.'.join([
                    data['schemaname'],
                    data['relname']
                ])
                if depth == 1:
                    ns.views.add(entity)
                else:
                    ns.dependencies.add(entity)
            else:
                for key, value in data.items():
                    inner(value, depth)
        elif isinstance(data, list) or isinstance(data, tuple):
            for item in data:
                inner(item, depth + 1)

    parsed_content = parse(content)
    inner(parsed_content, 0)
    return {
        'views': ns.views,
        'dependencies': ns.dependencies - ns.views
    }

def walk_directory_recursively(input_dir):
    file_paths = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            file_paths.append(os.path.join(root, file))
    return file_paths

def process_file(file_name, pattern):
    with open(file_name, 'r') as f:
        file_name = f.name
        content = f.read()
        nodes = extract_nodes(content, pattern)

        return {
            'file_name': file_name,
            'content': content,
            'views': nodes['views'],
            'view_dependencies': nodes['dependencies']
        }

def format_content(entity):
    file_name = entity['file_name']
    content_no_txn = entity['content'] \
        .replace('BEGIN;', '') \
        .replace('COMMIT;', '')
    return "  -- %s%s" % (file_name, content_no_txn)

def generate_script(views, spacer=''):
    return "\n\n".join([
        'BEGIN;',
        spacer.join(views),
        'COMMIT;'
    ])

def serialize_script(name, suffix, content, output_dir, verbose):
    script_name = '%s-%s.sql' % (name, suffix)
    script_path = os.path.join(output_dir, script_name)
    with open(script_path, 'w') as f:
        f.write(content)
        if verbose:
            print('Successfully saved "%s script" to "%s"' % (name, script_path))


@click.command()
@click.option('-d', '--dry-run', is_flag=True, help='Analyzes dependencies without actually generating the output files')
@click.option('-i', '--input-dir', default='.', help='The directory for the PostgreSQL scripts to analyze')
@click.option('-I', '--ignore-refresh', default='_v|hist', help='Regex pattern to match when ignoring refresh on Materialized Views (i.e. "_v|hist" for both "users_mv_hist" and "users_v")')
@click.option('-o', '--output-dir', default='.', help='Output directory for the generated creation and refresh scripts')
@click.option('-p', '--pattern', default='_m?v', help='View regex pattern to match (i.e. "_m?v" for both "users_mv_hist" and "users_v")')
@click.option('-v', '--verbose', is_flag=True, help='Enables verbose logging')
def cli(dry_run, input_dir, ignore_refresh, output_dir, pattern, verbose):

    dag = {}

    file_paths = walk_directory_recursively(input_dir)

    if verbose:
        print('Found %d Scripts in %s' % (len(file_paths), input_dir))

    entities = pipe(file_paths,
        map(lambda file_path: process_file(file_path, pattern)),
        list
    )

    if verbose:
        total_views = pipe(entities,
            map(get('views')),
            map(count),
            sum
        )
        total_deps = pipe(entities,
            map(get('view_dependencies')),
            map(count),
            sum
        )
        print('Identified %d Materialized Views, Containing %d View Dependencies' % (total_views, total_deps))

    view_content = {}
    dag = {}
    for entity in entities:
        view_content.update(
            {view: format_content(entity) for view in entity['views']}
        )
        dag.update(
            {view: entity['view_dependencies'] for view in entity['views']}
        )

    sorted_views = toposort_flatten(dag)

    if verbose:
        print("\nMaterialized View Dependencies:")
        pprint_color(
            valmap(lambda val: list(val), valfilter(lambda val: val, dag))
        )

    create_views = pipe(sorted_views,
        map(lambda view: view_content[view]),
        unique,
        list
    )

    create_script = generate_script(create_views)

    refresh_views = pipe(sorted_views,
        filter(lambda view: re.search(pattern, view) and not (ignore_refresh and re.search(ignore_refresh , view))),
        map(lambda view: '  REFRESH MATERIALIZED VIEW CONCURRENTLY ' + view + ';'),
        list
    )

    if verbose:
        print('Selecting %d Materialized Views for Refresh' % len(refresh_views))

    refresh_script = generate_script(refresh_views, "\n\n")

    if dry_run:
        print('Dry Run Option Enabled - Skipping Script Generation')
        return

    timestr = time.strftime("%Y%m%d-%H%M%S")

    serialize_script('create', timestr, create_script, output_dir, verbose)
    serialize_script('refresh', timestr, refresh_script, output_dir, verbose)
