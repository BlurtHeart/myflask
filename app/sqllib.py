#!/usr/bin/env python
import sqlite3

class DataBaseClient(object):
    def __init__(self, path='data-base.db'):
        self.path = path
        try:
            self.conn = sqlite3.connect(self.path)
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
            cur.execute(sql)
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
            result = cur.fetchone()
        except Exception as e:
            print(e)
            result = {}
        return result
    def fetchall(self):
        cursor = self.get_cursor()
        if cursor is None:
            return []
        try:
            result = cur.fetchall()
        except Exception as e:
            print(e)
            result = []
        return result    
        