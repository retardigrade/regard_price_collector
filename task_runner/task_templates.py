import os
from luigi.contrib import postgres

env_vars = os.environ
POSTGRES_HOST = env_vars['POSTGRES_HOST']
DATABASE_NAME = env_vars['DATABASE_NAME']
POSTGRES_USER = env_vars['POSTGRES_USER']
POSTGRES_PASSWORD = env_vars['POSTGRES_PASSWORD']
PROXY_TABLE_NAME = 'tmp'


class PostgresCopyToTableWithCredentials(postgres.CopyToTable):
    host = POSTGRES_HOST
    database = DATABASE_NAME
    user = POSTGRES_USER
    password = POSTGRES_PASSWORD
    table = PROXY_TABLE_NAME  # tmp table by default, can be overriden


class PostgresQueryWithCredentials(postgres.PostgresQuery):
    host = POSTGRES_HOST
    database = DATABASE_NAME
    user = POSTGRES_USER
    password = POSTGRES_PASSWORD
    table = PROXY_TABLE_NAME
    query = ''  # will be overriden anyway
