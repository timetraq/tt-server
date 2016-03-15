"""
Base Class for a mountable API
"""

from json import dumps, loads
from time import time
from uuid import uuid4

from flask import Flask
from redis import StrictRedis

from ...util.config import ConfigurationFileFinder
from ...util.queue.redis import RedisQueueProducer


class MountableAPI(object):
    """
    Provide a basic class for supporting mountable API endpoints
    """

    def __init__(self):
        """
        Prepare Queues
        """
        self.__config = ConfigurationFileFinder().find_as_json()['tts']['queues']['api']
        self.__queue = RedisQueueProducer(self.__config)

    def mount(self, namespace: str, application: Flask) -> None:
        """
        Mount application endpoints

        :param namespace: The mount point namespace
        :param application: The flask application
        :raises NotImplementedError: when not implemented
        """
        raise NotImplementedError

    def queue_dispatcher(self, message: dict) -> dict:
        """
        Dispatch a request to queue

        :param message: Message to dispatch
        :return: JSON data in return as dict
        :rtype: dict
        """
        uuid = str(uuid4())
        redis = StrictRedis(connection_pool=self.__queue.connection_pool)
        pubsub = redis.pubsub()
        message['_uuid'] = uuid
        message['_time'] = time()
        queue = 'req_{:s}'.format(uuid)
        pubsub.subscribe(queue)
        self.__queue.fire_message(dumps(message).encode('utf-8'))
        tries = 0
        while tries < 3:
            tries += 1
            message = pubsub.get_message(ignore_subscribe_messages=True, timeout=7.5)
            if message is not None:
                break
        pubsub.unsubscribe(queue)
        if message is None:
            return {
                'error': {
                    'code': -1,
                    'message': 'timeout',
                }
            }
        return loads(message['data'].decode('utf-8'), encoding='utf-8')

    @staticmethod
    def get_ip(request) -> str:
        """
        Get the IP address – helps to implement a new method when needed

        :param request: Request Object
        :return: IP Address
        :rtype: str
        """
        return request.remote_addr
