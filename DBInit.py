import sqlite3
from sqlite3 import Error


class DBInit(object):

    @staticmethod
    def create_connection(db_file):
        """
        create a database connection to a SQLite database
        :return connection to db
        """
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            print(e)
            return None

    @staticmethod
    def create_books_db(db_file):
        """
        creates books table
        :param db_file:
        :return:
        """
        conn = DBInit.create_connection(db_file)
        books_table_sql = """ CREATE TABLE IF NOT EXISTS books (
                                        id TEXT PRIMARY KEY,
                                        title TEXT NOT NULL,
                                        coverURL TEXT NOT NULL,
                                        ReleaseDate TEXT,
                                        language TEXT,
                                        author TEXT NOT NULL,
                                        authorKey TEXT NOT NULL,
                                        illustrator TEXT,
                                        category TEXT NOT NULL,
                                        locations TEXT NOT NULL,
                                        locationsDict TEXT NOT NULL                                       
                                    ); """
        DBInit.create_table(conn, books_table_sql)
        conn.close()

    @staticmethod
    def create_table(conn, create_table_sql):
        """
        create a table from the create_table_sql statement
        :param conn: Connection object
        :param create_table_sql: a CREATE TABLE statement
        :return:
        """
        try:
            c = conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)
