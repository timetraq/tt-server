# pylint: disable=too-many-public-methods
"""
Test the Redis Queue superclass
"""

from unittest import TestCase
from redis import StrictRedis
from redis.exceptions import ConnectionError as RedisConnectionError
from ...util.config import ConfigurationFileFinder
from ...util.queue.redis import RedisQueue
from ...util.singleton import SingletonMeta


class RedisQueueTest(TestCase):
    """
    Class Tests
    """

    @classmethod
    def tearDownClass(cls):
        """
        Clean up singleton instances of the Configuration File Finder
        """
        SingletonMeta.delete(ConfigurationFileFinder)

    def test_no_config(self) -> None:
        """
        An exception should be thrown when initializing with no configuration
        """
        self.assertRaises(TypeError, RedisQueue)

    def test_none_config(self) -> None:
        """
        An exception should be thrown when initializing with ``None`` configuration
        """
        self.assertRaises(ValueError, RedisQueue, None)

    def test_config_without_queue_name(self) -> None:
        """
        An exception should be thrown when initializing with incomplete configuration
        """
        config = {
            'host': '127.0.0.1',
            'port': 1234,
        }
        self.assertRaises(ValueError, RedisQueue, config)

    def test_default_settings(self):
        """
        With an Queue name, a url should be able to build up with default values
        """
        config = {
            'queue': 'PYTTS_TEST_QUEUE',
        }
        redis_queue = RedisQueue(config)
        url = redis_queue.build_url()
        # The URL scheme is defined in the Redis documentation
        # For default, we want localhost, default port, default db number, no password
        self.assertEqual(
            'redis://@localhost:6379/0',
            url
        )

    def test_changed_host(self) -> None:
        """
        Change the host and test
        """
        config = {
            'queue': 'PYTTS_TEST_QUEUE',
            'host': 'testhost.local',
        }
        redis_queue = RedisQueue(config)
        url = redis_queue.build_url()
        self.assertEqual(
            'redis://@testhost.local:6379/0',
            url
        )

    def test_changed_port(self) -> None:
        """
        Change the port and test
        """
        config = {
            'queue': 'PYTTS_TEST_QUEUE',
            'port': 1234,
        }
        redis_queue = RedisQueue(config)
        url = redis_queue.build_url()
        self.assertEqual(
            'redis://@localhost:1234/0',
            url
        )

    def test_changed_db(self) -> None:
        """
        Change the db and test
        """
        config = {
            'queue': 'PYTTS_TEST_QUEUE',
            'db': 5,
        }
        redis_queue = RedisQueue(config)
        url = redis_queue.build_url()
        self.assertEqual(
            'redis://@localhost:6379/5',
            url
        )

    def test_changed_queue(self) -> None:
        """
        Change the queue and test
        """
        config = {
            'queue': 'PYTTS_TEST_QUEUE_2',
        }
        redis_queue = RedisQueue(config)
        url = redis_queue.build_url()
        self.assertEqual(
            'redis://@localhost:6379/0',
            url
        )

    def test_changed_auth(self) -> None:
        """
        Change the auth and test
        """
        config = {
            'queue': 'PYTTS_TEST_QUEUE',
            'auth': 'supersecret',
        }
        redis_queue = RedisQueue(config)
        url = redis_queue.build_url()
        self.assertEqual(
            'redis://:supersecret@localhost:6379/0',
            url
        )

    def test_changed_socket(self) -> None:
        """
        Change the socket and test
        """
        config = {
            'queue': 'PYTTS_TEST_QUEUE',
            'socket': '/var/run/redis-socket.sock',
        }
        redis_queue = RedisQueue(config)
        url = redis_queue.build_url()
        self.assertEqual(
            'unix://@/var/run/redis-socket.sock?db=0',
            url
        )

    def test_socket_changed_host(self) -> None:
        """
        Change the host and test (socket mode)
        """
        config = {
            'queue': 'PYTTS_TEST_QUEUE',
            'socket': '/var/run/redis-socket.sock',
            'host': 'testhost.local',
        }
        redis_queue = RedisQueue(config)
        url = redis_queue.build_url()
        self.assertEqual(
            'unix://@/var/run/redis-socket.sock?db=0',
            url
        )

    def test_socket_changed_port(self) -> None:
        """
        Change the port and test (socket mode=
        """
        config = {
            'queue': 'PYTTS_TEST_QUEUE',
            'socket': '/var/run/redis-socket.sock',
            'port': 1234,
        }
        redis_queue = RedisQueue(config)
        url = redis_queue.build_url()
        self.assertEqual(
            'unix://@/var/run/redis-socket.sock?db=0',
            url
        )

    def test_socket_changed_db(self) -> None:
        """
        Change the port and test (socket mode=
        """
        config = {
            'queue': 'PYTTS_TEST_QUEUE',
            'socket': '/var/run/redis-socket.sock',
            'db': 9,
        }
        redis_queue = RedisQueue(config)
        url = redis_queue.build_url()
        self.assertEqual(
            'unix://@/var/run/redis-socket.sock?db=9',
            url
        )

    def test_socket_changed_queue(self) -> None:
        """
        Change the queue and test (socket mode)
        """
        config = {
            'queue': 'PYTTS_TEST_QUEUE_2',
            'socket': '/var/run/redis-socket.sock',
        }
        redis_queue = RedisQueue(config)
        url = redis_queue.build_url()
        self.assertEqual(
            'unix://@/var/run/redis-socket.sock?db=0',
            url
        )

    def test_socket_changed_auth(self) -> None:
        """
        Change the queue and test (socket mode)
        """
        config = {
            'queue': 'PYTTS_TEST_QUEUE',
            'socket': '/var/run/redis-socket.sock',
            'auth': 'secretcode'
        }
        redis_queue = RedisQueue(config)
        url = redis_queue.build_url()
        self.assertEqual(
            'unix://:secretcode@/var/run/redis-socket.sock?db=0',
            url
        )

    def test_changed_multiple(self) -> None:
        """
        Change multiple values and test
        """
        config = {
            'queue': 'PYTTS_TEST_QUEUE_3',
            'db': 8,
            'auth': 'keep-me-secret',
            'host': 'redis-server',
            'port': 4321,
        }
        redis_queue = RedisQueue(config)
        url = redis_queue.build_url()
        self.assertEqual(
            'redis://:keep-me-secret@redis-server:4321/8',
            url
        )

    def test_socket_changed_multiple(self) -> None:
        """
        Change multiple values and test (socket mode)
        """
        config = {
            'queue': 'PYTTS_TEST_QUEUE_4',
            'db': 7,
            'auth': 'do-not-use',
            'host': 'redis-socket-server',
            'port': 7890,
            'socket': '/var/run/redis-test-socket.sock',
        }
        redis_queue = RedisQueue(config)
        url = redis_queue.build_url()
        self.assertEqual(
            'unix://:do-not-use@/var/run/redis-test-socket.sock?db=7',
            url
        )

    def test_connection_pool_with_default_settings(self) -> None:
        """
        Use the settings that are already validated via Smoke Test to check the Connection Pool creation

        Basically, this repeats the test from the Smoke Tests, but now using the RedisQueue implementation
        """
        config = ConfigurationFileFinder().find_as_json()
        redis_config = config['tts']['queues']['command']
        redis_queue = RedisQueue(redis_config)
        pool = redis_queue.create_redis_connection_pool()
        redis_connection = StrictRedis(connection_pool=pool)
        self.assertEqual(
            b'test',
            redis_connection.echo(b'test')
        )
        del redis_connection

    def test_connection_pool_with_invalid_settings(self) -> None:
        """
        Use invalid settings to check the Connection Pool creation
        """
        config = {
            'queue': 'PYTTS_TEST_QUEUE_3',
            'db': 8,
            'auth': 'keep-me-secret',
            'host': 'redis-server-that-does-not-exist.local',
            'port': 4321,
        }
        redis_queue = RedisQueue(config)
        pool = redis_queue.create_redis_connection_pool()
        redis_connection = StrictRedis(connection_pool=pool)
        self.assertRaises(RedisConnectionError, redis_connection.echo, b'test')

    def test_independence(self) -> None:
        """
        Instances of RedisQueue shall be independent.

        Creating one with a socket and one without.
        """
        config_one = {
            'queue': 'PYTTS_TEST_QUEUE_1',
            'host': 'test-redis.local',
        }
        config_two = {
            'queue': 'PYTTS_TEST_QUEUE_2',
            'host': 'test-redis-1.local',
            'db': 5,
            'socket': '/var/run/redis-test.sock',
            'auth': 'supersecret1',
        }
        rq1 = RedisQueue(config_one)
        rq2 = RedisQueue(config_two)
        self.assertNotEqual(rq1, rq2)
        url1 = rq1.build_url()
        url2 = rq2.build_url()
        self.assertNotEqual(url1, url2)
