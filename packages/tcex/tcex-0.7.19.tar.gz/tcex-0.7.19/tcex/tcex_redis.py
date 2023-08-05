# -*- coding: utf-8 -*-
""" TcEx Framework Redis Module """
from builtins import str

import redis


class TcExRedis(object):
    """Create/Read Data in/from Redis"""

    def __init__(self, host, port, rhash):
        """ """
        self._hash = rhash
        # self._r = redis.StrictRedis(host=host, port=port, db=0)
        self._r = redis.StrictRedis(host=host, port=port)

    def create(self, key, value):
        """Create key/value pair in Redis"""
        return self._r.hset(self._hash, key, value)

    def delete(self, key):
        """Delete data from Redis for the provided key"""
        return self._r.hdel(self._hash, key)

    def read(self, key):
        """Read data from Redis for the provided key"""
        data = self._r.hget(self._hash, key)
        if data is not None and not isinstance(data, str):
            data = str(self._r.hget(self._hash, key), 'utf-8')
        return data
