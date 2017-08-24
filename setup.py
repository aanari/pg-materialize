import os
from setuptools import setup, find_packages

version = '0.2.4'

description = 'Postgres Materialized View Dependency Manager'

try:
    import pypandoc
    long_description = lambda f: pypandoc.convert(f, 'rst', format='md')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    long_description = lambda f: open(f, 'r').read()
except:
    long_description = description

setup(
    name='pg-materialize',
    version=version,
    description=description,
    long_description=long_description('README.md'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Database',
        'Topic :: Utilities'
    ],
    keywords='pg postgres psql pgsql postgresql materialized view dependency dependencies tool',
    url='http://github.com/aanari/pg-materialize',
    author='Ali Anari',
    author_email='ali@anari.io',
    license='MIT',
    packages=find_packages('pg_materialize'),
    include_package_data=True,
    package_dir={'': 'pg_materialize'},
    entry_points="""
        [console_scripts]
        pg_materialize = pg_materialize.pg_materialize:cli
    """,
    install_requires=[
        'click',
        'psqlparse==1.0rc5',
        'pypandoc',
        'Pygments',
        'six',
        'toolz',
        'toposort'
    ]
)
