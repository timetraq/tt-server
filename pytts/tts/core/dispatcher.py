# pylint: disable=too-few-public-methods
"""
Core Dispatcher for working from the Queue
"""

from json import loads, dumps
from time import time

from redis import StrictRedis

from .registry import FUNCTIONS
from ..util.config import ConfigurationFileFinder
from ..util.queue.redis import RedisQueueConsumer, RedisQueueAccess
from ..util.singleton import SingletonMeta


class DispatcherThread:
    """
    Simple Dispatcher Thread
    """

    def __init__(self, access: RedisQueueAccess):
        """
        Setup access to the Redis Queues

        :param access: The Redis Queue Access
        """
        self.__access = access

    def __call__(self, workload: bytes) -> None:
        """
        Call with workload

        :param workload: The workload to handle
        """
        data = loads(workload.decode('utf-8'), encoding='utf-8')
        if '_' not in data or '_uuid' not in data or '_time' not in data or 'data' not in data:
            return
        max_age = time() - 20
        if data['_time'] < max_age:
            return
        if data['_'] in FUNCTIONS:
            response = FUNCTIONS[data['_']](data['data'])
        else:
            response = {
                'error': {
                    'code': -2,
                    'message': 'unexported function',
                }
            }
        redis = StrictRedis(connection_pool=self.__access.connection_pool)
        redis.publish('req_{:s}'.format(data['_uuid']), dumps(response))


class CoreDispatcher(metaclass=SingletonMeta):
    """
    Build Core Dispatcher workers
    """

    __dispatchers = []
    __access = None

    def __init__(self):
        """
        Setup parallel workers
        """
        config = ConfigurationFileFinder().find_as_json()['tts']
        number_of_threads = 5
        if 'mumber_of_threads' in config:
            number_of_threads = config['number_of_threads']
        queue_conf = config['queues']['api']
        self.__access = RedisQueueAccess(queue_conf)
        for dummy in range(number_of_threads):
            consumer = RedisQueueConsumer(daemon=True, configuration=queue_conf,
                                          callback=DispatcherThread(self.__access))
            self.__dispatchers.append(consumer)
