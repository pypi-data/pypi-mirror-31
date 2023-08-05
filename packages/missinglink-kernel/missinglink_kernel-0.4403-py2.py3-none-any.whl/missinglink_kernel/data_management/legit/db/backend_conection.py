# -*- coding: utf8 -*-
from .base_connection import BaseConnection
import requests


class BackendConnection(BaseConnection):
    def __init__(self, data_volume_config, **kwargs):
        super(BackendConnection, self).__init__(data_volume_config, **kwargs)

    def _create_connection(self, **kwargs):
        return requests

    def _create_cursor(self):
        return requests.session()

    def _rollback(self):
        raise NotImplementedError(self._rollback)

    def create_sql_helper(self):
        raise NotImplementedError(self.create_sql_helper)

    def _commit(self):
        raise NotImplementedError(self._commit)
