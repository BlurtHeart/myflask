# -*- coding:utf-8 -*-
"""
    sqllib
    ~~~~~~~~~~~~~~~~~~~

    general databaseclient for sqlite3.

    :copyright: (c) 2017 by Blurt Heart.
    :license: BSD, see LICENSE for more details.
"""
import sqlite3

__all__ = ['DataBaseClient']

def dict_factory(cursor, row): 
  d = {} 
  for idx, col in enumerate(cursor.description): 
    d[col[0]] = row[idx] 
  return d

class DataBaseClient(object):
    def __init__(self, path='data-dev.sqlite'):
        self.path = path
        try:
            self.conn = sqlite3.connect(self.path)
            self.conn.row_factory = dict_factory
            self.cur = self.conn.cursor()
        except Exception as e:
            print(e)
            self.conn = None
            self.cur = None
    def connect(self):
        conn = getattr(self, 'conn', None)
        cursor = getattr(self, 'cur', None)
        try:
            if conn is None:
                self.conn = sqlite3.connect(self.path)
            if cursor is None:
                self.cur = self.conn.cursor()
        except Exception as e:
            print(e)
            self.conn = None
            self.cur = None
    def __enter__(self):
        return self
    def __exit__(self, Type, value, traceback):
        if not self.cur:
            self.cur.close()
        if not self.conn:
            self.conn.close()
    def get_cursor(self):
        cursor = getattr(self, 'cursor', None)
        if cursor is None:
            self.connect()
        return self.cur
    def get_conn(self):
        conn = getattr(self, 'conn', None)
        if conn is None:
            self.connect()
        return self.conn
    def execute(self, sql):
        cursor = self.get_cursor()
        conn = self.get_conn()
        if cursor is None or conn is None:
            return 0
        try:
            cursor.execute(sql)
            conn.commit()
            return 1
        except Exception as e:
            print(e)
            return 0
    def fetchone(self):
        cursor = self.get_cursor()
        if cursor is None:
            return {}
        try:
            result = cursor.fetchone()
        except Exception as e:
            print(e)
            result = {}
        return result
    def fetchall(self):
        cursor = self.get_cursor()
        if cursor is None:
            return []
        try:
            result = cursor.fetchall()
        except Exception as e:
            print(e)
            result = []
        return result    
        