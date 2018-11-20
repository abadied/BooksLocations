import sqlite3
from sqlite3 import Error


class DBHandler(object):

    def __init__(self, db_file):
        try:
            self.conn = sqlite3.connect(db_file)
        except Error as e:
            print(e)

    def insert_to_books(self, *args):
        sql = ''' INSERT INTO books(id,name,author,locations,genre,releaseDate,language,url)
                  VALUES(?,?,?,?,?,?,?,?) '''
        cur = self.conn.cursor()
        try:
            cur.execute(sql, args)
        except Error as e:
            print(e)

    def delete_from_books_by_name(self, name_key):
        sql = ''' Delete FROM books Where name=?'''
        cur = self.conn.cursor()
        try:
            cur.execute(sql, (name_key,))
        except Error as e:
            print(e)

    def drop_table(self, table_name):
        cur = self.conn.cursor()
        sql = 'DROP TABLE' + table_name
        try:
            cur.execute(sql)
        except Error as e:
            print(e)

    def get_from_books_by_name(self, name_key):
        sql = ''' SELECT * FROM books WHERE name=? '''
        cur = self.conn.cursor()
        try:
            cur.execute(sql, (name_key,))
            return cur.fetchall()
        except Error as e:
            print(e)
            return None

    def update_books_by_name(self, name, author, locations, genre, releaseDate, language, url):
        sql = ''' UPDATE books SET author = ? ,
                                   locations = ?,
                                   genre = ?,
                                   releaseDate = ?,
                                   language = ?,
                                   url = ?
                  WHERE name = ? '''
        cur = self.conn.cursor()
        try:
            cur.execute(sql, (author, locations, genre, releaseDate, language, url,))
        except Error as e:
            print(e)