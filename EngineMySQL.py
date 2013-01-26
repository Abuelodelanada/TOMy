#! /usr/bin/env python
# -*- coding: utf-8 -*-


class EngineMySQL():
    """
    """
    def __init__(self):
        """
        """
    def server_info(self, connection):
        """
        Shows the server info
        """
        server_info = connection.get_server_info()
        server_status = connection.stat()
        server_connection_id = connection.thread_id()
        server_data = [server_info, server_status, server_connection_id]
        return server_data

    def get_databases(self, cursor):
        """
        Get the names of the databases in the server.
        """
        query = 'SELECT SCHEMA_NAME FROM information_schema.SCHEMATA'
        cursor.execute(query)
        result = cursor.fetchall()
        databases = []
        for db in result:
            databases.append(db[0])
        return databases

    def get_tables(self, cursor, db):
        """
        Get the tables names
        """
        query = '''SELECT information_schema.TABLES.TABLE_NAME
                   FROM information_schema.TABLES
                   WHERE information_schema.TABLES.TABLE_SCHEMA = "%s"''' % db
        cursor.execute(query)
        result = cursor.fetchall()
        tables = []
        for table in result:
            tables.append(table[0])
        return tables

    def get_columns(self, cursor, db):
        """
        Get the fields names
        """
        query = '''SELECT information_schema.COLUMNS.COLUMN_NAME
                   FROM information_schema.COLUMNS
                   WHERE information_schema.COLUMNS.TABLE_SCHEMA = "%s"''' % db
        cursor.execute(query)
        result = cursor.fetchall()
        columns = []
        for column in result:
            columns.append(column[0])
        return columns
