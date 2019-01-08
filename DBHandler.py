import sqlite3
from sqlite3 import Error


class DBHandler(object):

    def __init__(self, db_file):
        try:
            self.conn = sqlite3.connect(db_file)
        except Error as e:
            print(e)

    def insert_to_books(self, args):
        sql = ''' INSERT INTO books(id,title,coverURL, ReleaseDate, language, author, authorKey,
         illustrator, category, locations)
                  VALUES(?,?,?,?,?,?,?,?,?,?) '''
        cur = self.conn.cursor()
        try:
            cur.execute(sql, args)
            self.conn.commit()
        except Error as e:
            print(e)

    def delete_from_books_by_name(self, name_key):
        sql = ''' Delete FROM books Where title=?'''
        cur = self.conn.cursor()
        try:
            cur.execute(sql, (name_key,))
            self.conn.commit()
        except Error as e:
            print(e)

    def drop_table(self, table_name):
        cur = self.conn.cursor()
        sql = 'DROP TABLE' + table_name
        try:
            cur.execute(sql)
            self.conn.commit()
        except Error as e:
            print(e)

    def get_from_books_by_name(self, name_key):
        sql = ''' SELECT * FROM books WHERE title=? '''
        cur = self.conn.cursor()
        try:
            cur.execute(sql, (name_key,))
            return cur.fetchall()
        except Error as e:
            print(e)
            return None

    def get_all_books(self):
        sql = ''' SELECT * FROM books'''
        cur = self.conn.cursor()
        try:
            cur.execute(sql)
            return cur.fetchall()
        except Error as e:
            print(e)
            return None

    def update_books_by_name(self, title, *args):
        sql = ''' UPDATE books SET coverURL = ?,
                                   ReleaseDate = ?,
                                   language = ?,
                                   author = ?,
                                   authorKey = ?,
                                   illustrator = ?,
                                   category = ?,
                                   locations = ?
                  WHERE title = ''' + title
        cur = self.conn.cursor()
        try:
            cur.execute(sql, args)
            self.conn.commit()
        except Error as e:
            print(e)