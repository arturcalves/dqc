import pyodbc
import psycopg2
import pymysql

CONNECTION_DRIVER_CHOICES = (
    ('mysql', 'MySQL'),
    ('pgsql', 'PostgreSQL'),
    ('mssql', 'Microsoft SQL Server'),
)


def get_column_type(type):
    if type in [str, 'character varying', 'text']:
        return 'String'
    elif type in [int, float, 'integer', 'bigint']:
        return 'Number'
    elif type in ['date', 'timestamp', 'timestamp without time zone']:
        return 'Date'
    elif type in [bool, 'boolean']:
        return 'Boolean'
    if type in [bytearray, bytes, 'bytea']:
        return 'Binary'
    else:
        # return 'UNDEFINED'
        return type


class MyDB(object):
    _db_connection = None
    _db_cur = None
    con_string = ""

    def __init__(self, dataset):
        if dataset.connection_driver == 'mysql':
            self._db_connection = pymysql.connect(host=dataset.connection_server,
                                                  port=dataset.connection_port,
                                                  user=dataset.connection_user,
                                                  passwd=dataset.connection_password,
                                                  db=dataset.connection_database)
        elif dataset.connection_driver == 'pgsql':
            con_string = 'host=%s port=%s user=%s password=%s dbname=%s' % (dataset.connection_server,
                                                                            dataset.connection_port,
                                                                            dataset.connection_user,
                                                                            dataset.connection_password,
                                                                            dataset.connection_database)
            self._db_connection = psycopg2.connect(con_string)

        elif dataset.connection_driver == 'mssql':
            # con_string = 'DSN=%s;UID=%s;PWD=%s;DATABASE=%s;' % ('sqlserverdatasource',
            #                                                                  dataset.connection_user,
            #                                                                  dataset.connection_password,
            #                                                                  dataset.connection_database)
            con_string = 'DRIVER=FreeTDS;SERVER=%s;PORT=%s;UID=%s;PWD=%s;DATABASE=%s;' % \
                         (dataset.connection_server,
                          dataset.connection_port,
                          dataset.connection_user,
                          dataset.connection_password,
                          dataset.connection_database)
            self._db_connection = pyodbc.connect(con_string)

        self._db_cur = self._db_connection.cursor()

    def query(self, query, params=None):
        if params:
            self._db_cur.execute(query, params)
        else:
            self._db_cur.execute(query)
        return self._db_cur

    def __del__(self):
        self._db_connection.close()

    def __str__(self):
        self.con_string

def is_connecting(dataset):
    try:
        db = MyDB(dataset)
        results = db.query("SELECT VERSION()").fetchone()
        if results:
            return True
    except:
        return False

    return False


def get_table_list(dataset):
    db = MyDB(dataset)
    if dataset.connection_driver == 'mssql':
        rows = db.query('SELECT table_name FROM information_schema.tables').fetchall()
    elif dataset.connection_driver == 'pgsql':
        rows = db.query("select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';").fetchall()
    tables = []
    for row in rows:
        tables += [row[0]]
    tables.sort()
    return tables


# def get_table_list(dataset):
#     if dataset.connection_driver == 'SQLServer':
#     #if True:
#         dsn = 'sqlserverdatasource'
#         user = 'sinapse'
#         password = '51n4p53dbmS'
#         database = 'SISTEMA_ACADEMICO'
#
#         con_string = 'DSN=%s;UID=%s;PWD=%s;DATABASE=%s;' % (dsn, user, password, database)
#         try:
#             cnxn = pyodbc.connect(con_string)
#         except:
#             return []
#
#         cursor = cnxn.cursor()
#         cursor.execute('SELECT * FROM information_schema.tables')
#         rows = cursor.fetchall()
#         tables = []
#         for row in rows:
#             tables += [row[2]]
#     else:
#         tables = ['bananaa', 'maça', 'abacaxi', 'beterraba']
#     tables.sort()
#     return tables



def get_column_list(datatable):
    db = MyDB(datatable.data_set)
    columns = []
    if datatable.data_set.connection_driver == 'mssql':
        descriptions = db.query('select top 1 * from %s ;' % datatable.name).description
        for desc in descriptions:
            columns += [(desc[0], get_column_type(desc[1]))]
    elif datatable.data_set.connection_driver == 'pgsql':
        descriptions = db.query("select column_name, data_type from information_schema.columns where table_name='%s';" % datatable.name)
        for desc in descriptions:
            columns += [(desc[0], get_column_type(desc[1]))]
    columns.sort()
    return columns
