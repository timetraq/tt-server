"""
Implement Queues with Redis
"""

import redis


class RedisQueue(object):
    """
    Basic configuration and methods for working with Redis
    """

    __use_socket = False
    __use_auth = False
    __host = 'localhost'
    __port = 6379
    __db = 0
    __socket = '/var/run/redis.sock'
    __auth = None
    __queue_key = None

    def __init__(self, configuration: dict):
        """
        Load configuration from dictionary. Can be easily used to work with parts of config files.

        :param dict configuration: Configuration to use
        :raises ValueError: when configuration is not sufficient
        """
        if configuration is None:
            raise ValueError('Configuration must be present. There are some keys that have not a valid default value.')
        if 'queue' not in configuration:
            raise ValueError('Queue Key must be set!')
        self.__queue_key = configuration['queue']
        if 'socket' in configuration and configuration['socket'] is not None:
            self.__use_socket = True
            self.__socket = configuration['socket']
        if 'auth' in configuration and configuration['auth'] is not None:
            self.__use_auth = True
            self.__auth = configuration['auth']
        if 'host' in configuration and configuration['host'] is not None:
            self.__host = configuration['host']
        if 'port' in configuration and configuration['port'] is not None:
            self.__port = configuration['port']
        if 'db' in configuration and configuration['db'] is not None:
            self.__db = configuration['db']

    def build_url(self) -> str:
        """
        Build a redis connection URL for creating a pool

        :return: A connection URL
        :rtype: str
        """
        if self.__use_socket:
            if self.__use_auth:
                redis_url = 'unix://:{:s}@{:s}?db={:d}'.format(self.__auth, self.__socket, self.__db)
            else:
                redis_url = 'unix://@{:s}?db={:d}'.format(self.__socket, self.__db)
        else:
            if self.__use_auth:
                redis_url = 'redis://:{:s}@{:s}:{:d}/{:d}'.format(self.__auth, self.__host, self.__port, self.__db)
            else:
                redis_url = 'redis://@{:s}:{:d}/{:d}'.format(self.__host, self.__port, self.__db)
        return redis_url

    def create_redis_connection_pool(self) -> redis.ConnectionPool:
        """
        Create a Redis ConnectionPool from the access data collected in this class

        :return: A redis connection pool build with the connection access data
        :rtype: redis.ConnectionPool
        """
        return redis.ConnectionPool.from_url(url=self.build_url())

    @property
    def queue(self) -> str:
        """
        Get the Queue key for this redis queue

        :return: The Redis Queue Key
        :rtype: str
        """
        return self.__queue_key
