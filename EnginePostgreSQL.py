#! /usr/bin/env python
# -*- coding: utf-8 -*-


class EnginePostgreSQL():
    """
    """
    def __init__(self):
        """
        """
    def server_info(self, connection):
        """
        Shows the server info
        """
        server_version = connection.server_version
        server_pid = connection.get_backend_pid()
        server_data = [str(server_version), str(server_pid)]
        return server_data
