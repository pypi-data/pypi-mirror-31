try:
    # Python 2
    from distutils import strtobool
except:
    # Python 3
    from distutils.util import strtobool
import logging
import sys
import traceback

import click
import psycopg2


logger = logging.getLogger(__name__)

DATABASE_CONNECTION_ERROR_MSG = 'Unable to connect to database. Postgres traceback:\n{}'

FAILED_QUERY_MSG = 'Failed to execute query "{}": {}'
UNSUPPORTED_CHAR_MSG = 'Role "{}" contains an unsupported character: \' or "'
PROGRESS_TEMPLATE = '%(label)s  [%(bar)s]  %(info)s'


def check_name(name):
    if "'" in name or '"' in name:
        fail(msg=UNSUPPORTED_CHAR_MSG.format(name))
    else:
        return name


def ensure_quoted_identifier(objname):
    """
    Ensure that all parts of an identifier after the first dot are surrounded by double quotes.
    This is necessary because Postgres will not accept identifiers with more than one dot in them
    unless they are constructed like this.

    How do identifiers like this come to be in the first place? A common scenario is someone
    accidentally creating an object like 'myschema.mytable' _within_ a schema, i.e. the
    schema-qualified object is myschema.myschema.mytable. Postgres won't accept a name like
    that, but it will accept myschema."myschema.mytable".
    """
    # This function is irrelevant if the object isn't schema-qualified
    if '.' not in objname:
        return objname

    schema, nonschema = objname.split('.', 1)
    if nonschema.startswith('"') and nonschema.endswith('"'):
        return objname

    return '{}."{}"'.format(schema, nonschema)


def fail(msg):
    click.secho(msg, fg='red')
    sys.exit(1)


def get_db_connection(host, port, dbname, user, password):
    try:
        db_conn = psycopg2.connect(host=host, port=port, dbname=dbname, user=user, password=password)
        db_conn.set_session(autocommit=False)
        return db_conn
    except Exception as e:
        fail(DATABASE_CONNECTION_ERROR_MSG.format(e))


def item_show_func(x):
    return x[0] if x else ''


def parse_bool(value):
    return bool(strtobool(str(value).lower()))


def run_query(cursor, verbose, query):
    logger.debug('Executing query: {}'.format(query))
    try:
        cursor.execute(query)
    except Exception as e:
        if verbose:
            click.secho(FAILED_QUERY_MSG.format(query, ''), fg='red')
            # The following is needed to output the traceback as well
            exc_type, exc_value, exc_tb = sys.exc_info()
            formatted_tb = '\n'.join(traceback.format_tb(exc_tb))
            click.secho(formatted_tb)
        else:
            click.secho(FAILED_QUERY_MSG.format(query, e), fg='red')
        sys.exit(1)
