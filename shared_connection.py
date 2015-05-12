import psycopg2
import psycopg2.extras

class SharedConnection(object):
    conninfo = None
    conn = None
    def __init__(self, conninfo=None, autocommit=True):
        if conninfo:
            SharedConnection.conninfo = conninfo
            if SharedConnection.conn:
                SharedConnection.conn.close()
                SharedConnection.conn = None
        if not SharedConnection.conninfo:
            raise TypeError('Never initialized with connection info!')
        if not SharedConnection.conn:
            SharedConnection.conn = psycopg2.connect(self.conninfo)
            SharedConnection.conn.autocommit = autocommit
            if not SharedConnection.conn:
                raise TypeError('Shared Connection unable to connect to database!')
    @classmethod
    def isOpen(cls):
        return SharedConnection.conn is not None
    @classmethod
    def close(cls):
        if cls.conn:
            cls.conn.close()
            cls.conn = None
    @classmethod
    def reset(cls):
        cls.close()
        cls.conninfo = None
        cls.conn = None
    @classmethod
    def _cursor(cls):
        """ If you call this you must call cursor.close() when you are done """
        if not SharedConnection.conn:
            raise TypeError('Shared Connection never initialized!')
        return SharedConnection.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    @classmethod
    def execute(cls, operation, parameters=None):
        with SharedConnection._cursor() as cursor:
            cursor.execute(operation, parameters)
            try:
                return cursor.fetchall()
            except psycopg2.ProgrammingError:
                return None
    @classmethod
    def mogrify(cls, operation, parameters=None):
        with SharedConnection._cursor() as cursor:
            return cursor.mogrify(operation, parameters)
    @classmethod
    def rollback(cls):
        SharedConnection.conn.rollback()
    @classmethod
    def commit(cls):
        SharedConnection.conn.commit()

