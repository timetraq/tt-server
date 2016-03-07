"""
Test Presence of Redis
"""

from unittest import TestCase
import redis
from ...util.config import ConfigurationFileFinder
from ...util.singleton import SingletonMeta


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
        assert 'test' in queues
        test = queues['test']
        assert isinstance(test, dict)
        assert 'db' in test
        assert 'queue' in test
        auth = None
        if 'auth' in test and test['auth'] is not None:
            auth = test['auth']
        if 'socket' in test and test['socket'] is not None:
            if auth is not None:
                redis_url = 'unix://:{:s}@{:s}?db={:d}'.format(auth, test['socket'], test['db'])
            else:
                redis_url = 'unix://@{:s}?db={:d}'.format(test['socket'], test['db'])
        else:
            assert 'host' in test
            assert 'port' in test
            if auth is not None:
                redis_url = 'redis://:{:s}@{:s}:{:d}/{:d}'.format(auth, test['host'], test['port'], test['db'])
            else:
                redis_url = 'redis://@{:s}:{:d}/{:d}'.format(test['host'], test['port'], test['db'])
        cls.__redis_pool = redis.ConnectionPool.from_url(url=redis_url)

    @classmethod
    def tearDownClass(cls):
        """
        Close the redis pool
        """
        del cls.__redis_pool
        del cls.__config
        SingletonMeta.delete(ConfigurationFileFinder)

    def test_smoke(self):
        """
        Simple Echo Test
        """
        redis_connection = redis.StrictRedis(connection_pool=self.__redis_pool)
        test = redis_connection.echo(b'test')
        self.assertEqual(test, b'test')
        del redis_connection
