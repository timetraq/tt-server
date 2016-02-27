"""
Test Presence of Redis
"""

from unittest import TestCase
import redis
from ...util.config import ConfigurationFileFinder


class RedisSmokeTest(TestCase):
    """
    Simple Smoke Test for Redis Access
    """

    @classmethod
    def setUpClass(cls):
        """
        Find configuration and create a Test Pool

        #    redis://[:password]@localhost:6379/0
        #    rediss://[:password]@localhost:6379/0
        #    unix://[:password]@/path/to/socket.sock?db=0
        """
        cls.__config = ConfigurationFileFinder().find_as_json()
        assert cls.__config is not None
        assert isinstance(cls.__config, dict)
        assert 'tts' in cls.__config
        tts = cls.__config['tts']
        assert isinstance(tts, dict)
        assert 'queues' in tts
        queues = tts['queues']
        assert isinstance(queues, dict)
        assert 'command' in queues
        command = queues['command']
        assert isinstance(command, dict)
        assert 'db' in command
        assert 'queue' in command
        auth = None
        if 'auth' in command and command['auth'] is not None:
            auth = command['auth']
        if 'socket' in command and command['socket'] is not None:
            if auth is not None:
                redis_url = 'unix://:{:s}@{:s}?db={:d}'.format(auth, command['socket'], command['db'])
            else:
                redis_url = 'unix://@{:s}?db={:d}'.format(command['socket'], command['db'])
        else:
            assert 'host' in command
            assert 'port' in command
            if auth is not None:
                redis_url = 'redis://:{:s}@{:s}:{:d}/{:d}'.format(auth, command['host'], command['port'], command['db'])
            else:
                redis_url = 'redis://@{:s}:{:d}/{:d}'.format(command['host'], command['port'], command['db'])
        cls.__redis_pool = redis.ConnectionPool.from_url(url=redis_url)

    @classmethod
    def tearDownClass(cls):
        """
        Close the redis pool
        """
        del cls.__redis_pool

    def test_connection(self):
        """
        Simple Echo Test
        """
        redis_connection = redis.Redis(connection_pool=self.__redis_pool)
        test = redis_connection.echo(b'test')
        self.assertEqual(test, b'test')
