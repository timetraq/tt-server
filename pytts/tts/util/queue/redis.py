"""
Implement Queues with Redis
"""

from threading import Thread
import redis


class RedisQueueConfiguration(object):
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


class RedisQueueAccess(RedisQueueConfiguration):
    """
    Access class for a Redis Queue
    """

    __pubsub_channel = None
    __connection_pool = None

    def __prepare(self) -> None:
        """
        Prepare the redis stuff

        :raises ValueError: When the queue is not of ``list`` type and not ``none``
        """
        redis_connection = self.get_connection()
        queue_type = redis_connection.type(self.queue)
        if queue_type == b'none':
            return
        if queue_type == b'list':
            return
        raise ValueError('Queue is not a list!')

    def __init__(self, configuration: dict):
        """
        Load configuration dictionary in a ``RedisQueueConfiguration`` and prepare the Queue for use

        :param dict configuration: Configuration
        """
        super(RedisQueueAccess, self).__init__(configuration)
        self.__pubsub_channel = '{:s}_PUBSUB_CH'.format(self.queue)
        self.__connection_pool = self.create_redis_connection_pool()
        self.__prepare()

    @property
    def pubsub_channel(self) -> str:
        """
        Get the Pub/Sub Channel name

        :return: The name of the Publish/Subscribe channel
        :rtype: str
        """
        return self.__pubsub_channel

    @property
    def connection_pool(self) -> str:
        """
        Get the connection pool

        :return: The name of the connection pool
        :rtype: str
        """
        return self.__connection_pool

    def get_connection(self) -> redis.StrictRedis:
        """
        Get a connection with the local connection pool

        :return: A redis connection
        :rtype: redis.StrictRedis
        """
        return redis.StrictRedis(connection_pool=self.connection_pool)


class RedisQueueConsumer(RedisQueueAccess):
    """
    Consume from a Redis Queue
    """

    __callback = None
    __should_run = True
    __watcher = None

    def __init__(self, configuration: dict, callback, daemon: bool=False):
        """
        Create a Redis Queue consumer with the configuration and a ``callback`` method.

        :param dict configuration: Configuration of the Queue
        :param callback: Callback Method
        :param bool daemon: Should the Consumer be a daemon
        """
        super(RedisQueueConsumer, self).__init__(configuration)
        self.__callback = callback
        self.work()
        self.__watcher = Thread(target=self.__listener, daemon=daemon)
        self.__watcher.start()

    def work(self) -> None:
        """
        Work Queue entries
        """
        redis_connection = self.get_connection()
        while self.__should_run:
            workload = redis_connection.lpop(self.queue)
            if workload is None:
                break
            self.__callback(workload)

    def __listener(self) -> None:
        """
        Wait for messages on the pubsub channel
        """
        redis_connection = self.get_connection()
        pubsub = redis_connection.pubsub()
        pubsub.subscribe(self.pubsub_channel)
        while self.__should_run:
            message = pubsub.get_message(ignore_subscribe_messages=True, timeout=.125)
            if message:
                self.work()
        pubsub.unsubscribe(self.pubsub_channel)

    def stop(self) -> None:
        """
        Stop the consumer
        """
        self.__should_run = False


class RedisQueueProducer(RedisQueueAccess):
    """
    Use this to fire messages into a queue
    """

    def __init__(self, configuration: dict):
        super(RedisQueueProducer, self).__init__(configuration)

    def fire_message(self, message: str) -> int:
        """
        Send a message to the queue

        :param str message: Message to be send
        :return: Number of clients that received the message
        :rtype: int
        """
        redis_connection = self.get_connection()
        redis_connection.rpush(self.queue, message)
        return redis_connection.publish(self.pubsub_channel, '1')
