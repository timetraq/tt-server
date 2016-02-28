# pylint: disable=too-many-public-methods
"""
Test the Redis Queue superclass
"""

from unittest import TestCase
from unittest.mock import Mock
from time import sleep

import pytest
from redis import StrictRedis
from redis.exceptions import ConnectionError as RedisConnectionError
from ...util.config import ConfigurationFileFinder
from ...util.queue.redis import RedisQueueAccess, RedisQueueConfiguration, RedisQueueConsumer, RedisQueueProducer
from ...util.singleton import SingletonMeta


class RedisQueueConfigurationTest(TestCase):
    """
    Class Tests
    """

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Clean up singleton instances of the Configuration File Finder
        """
        SingletonMeta.delete(ConfigurationFileFinder)

    def test_no_config(self) -> None:
        """
        An exception should be thrown when initializing with no configuration
        """
        self.assertRaises(TypeError, RedisQueueConfiguration)

    def test_none_config(self) -> None:
        """
        An exception should be thrown when initializing with ``None`` configuration
        """
        self.assertRaises(ValueError, RedisQueueConfiguration, None)

    def test_config_without_queue_name(self) -> None:
        """
        An exception should be thrown when initializing with incomplete configuration
        """
        config = {
            'host': '127.0.0.1',
            'port': 1234,
        }
        self.assertRaises(ValueError, RedisQueueConfiguration, config)

    def test_default_settings(self) -> None:
        """
        With an Queue name, a url should be able to build up with default values
        """
        config = {
            'queue': 'PYTTS_TEST_QUEUE',
        }
        redis_queue = RedisQueueConfiguration(config)
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
        redis_queue = RedisQueueConfiguration(config)
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
        redis_queue = RedisQueueConfiguration(config)
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
        redis_queue = RedisQueueConfiguration(config)
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
        redis_queue = RedisQueueConfiguration(config)
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
        redis_queue = RedisQueueConfiguration(config)
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
        redis_queue = RedisQueueConfiguration(config)
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
        redis_queue = RedisQueueConfiguration(config)
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
        redis_queue = RedisQueueConfiguration(config)
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
        redis_queue = RedisQueueConfiguration(config)
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
        redis_queue = RedisQueueConfiguration(config)
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
        redis_queue = RedisQueueConfiguration(config)
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
        redis_queue = RedisQueueConfiguration(config)
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
        redis_queue = RedisQueueConfiguration(config)
        url = redis_queue.build_url()
        self.assertEqual(
            'unix://:do-not-use@/var/run/redis-test-socket.sock?db=7',
            url
        )

    def test_connection_pool_with_default_settings(self) -> None:
        """
        Use the settings that are already validated via Smoke Test to check the Connection Pool creation

        Basically, this repeats the test from the Smoke Tests, but now using the RedisQueueConfiguration implementation
        """
        config = ConfigurationFileFinder().find_as_json()
        redis_config = config['tts']['queues']['command']
        redis_queue = RedisQueueConfiguration(redis_config)
        pool = redis_queue.create_redis_connection_pool()
        redis_connection = StrictRedis(connection_pool=pool)
        self.assertEqual(
            b'test',
            redis_connection.echo(b'test')
        )
        del redis_connection

    @pytest.mark.timeout(15)
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
        redis_queue = RedisQueueConfiguration(config)
        pool = redis_queue.create_redis_connection_pool()
        redis_connection = StrictRedis(connection_pool=pool)
        self.assertRaises(RedisConnectionError, redis_connection.echo, b'test')

    def test_independence(self) -> None:
        """
        Instances of RedisQueueConfiguration shall be independent.

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
        rq1 = RedisQueueConfiguration(config_one)
        rq2 = RedisQueueConfiguration(config_two)
        self.assertNotEqual(rq1, rq2)
        url1 = rq1.build_url()
        url2 = rq2.build_url()
        self.assertNotEqual(url1, url2)

    def test_queue_property(self) -> None:
        """
        Test that the queue property reflects the setting
        """
        config = {
            'queue': 'PYTTS_TEST_QUEUE-0',
        }
        redis_queue = RedisQueueConfiguration(config)
        self.assertEqual(
            'PYTTS_TEST_QUEUE-0',
            redis_queue.queue
        )

    def test_multiple_queue_properies(self) -> None:
        """
        Test the independence of these properties
        """
        config_one = {
            'queue': 'PYTTS_TEST_QUEUE-01',
        }
        config_two = {
            'queue': 'PYTTS_TEST_QUEUE-02',
        }
        redis_queue_one = RedisQueueConfiguration(config_one)
        redis_queue_two = RedisQueueConfiguration(config_two)
        self.assertEqual(
            'PYTTS_TEST_QUEUE-01',
            redis_queue_one.queue
        )
        self.assertEqual(
            'PYTTS_TEST_QUEUE-02',
            redis_queue_two.queue
        )


class RedisQueueAccessTest(TestCase):
    """
    Test the access class
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Setup the test class
        """
        SingletonMeta.delete(ConfigurationFileFinder)
        cls.__config = ConfigurationFileFinder().find_as_json()['tts']['queues']['command']
        cls.__redis = RedisQueueConfiguration(cls.__config)
        cls.__pool = cls.__redis.create_redis_connection_pool()
        StrictRedis(connection_pool=cls.__pool).flushdb()

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Clean up singleton instances of the Configuration File Finder and clear the database
        """
        StrictRedis(connection_pool=cls.__pool).flushdb()
        SingletonMeta.delete(ConfigurationFileFinder)

    def setUp(self) -> None:
        """
        Flush the database before running a test
        """
        StrictRedis(connection_pool=self.__pool).flushdb()

    def test_key_generation(self) -> None:
        """
        Test if the generated keys match the specification
        """
        base_name = self.__config['queue']
        pubsub_name = '{:s}_PUBSUB_CH'.format(base_name)
        rqa = RedisQueueAccess(self.__config)
        self.assertEqual(base_name, rqa.queue)
        self.assertEqual(pubsub_name, rqa.pubsub_channel)

    def test_preparation(self) -> None:
        """
        Test the preparation after initializing the class
        """
        rqa = RedisQueueAccess(self.__config)
        redis = StrictRedis(connection_pool=self.__pool)
        type_queue = redis.type(rqa.queue)
        type_pubsub = redis.type(rqa.pubsub_channel)
        self.assertEqual(type_queue, b'none')
        self.assertEqual(type_pubsub, b'none')

    def test_list_preparation_with_exisiting_list(self) -> None:
        """
        Test preparation with an already existing list
        """
        redis = StrictRedis(connection_pool=self.__pool)
        redis.lpush(self.__config['queue'], 'test')
        rqa = RedisQueueAccess(self.__config)
        type_queue = redis.type(rqa.queue)
        self.assertEqual(type_queue, b'list')

    def test_list_preparation_with_invalid_type(self) -> None:
        """
        When a list key is already there with a wrong type
        """
        redis = StrictRedis(connection_pool=self.__pool)
        redis.set(self.__config['queue'], 'test')
        self.assertRaises(ValueError, RedisQueueAccess, self.__config)

    def test_empty_list_contents_external(self) -> None:
        """
        Test if there comes nothing back when the list is empty (does the preparation work as expected?)
        """
        RedisQueueAccess(self.__config)
        redis = StrictRedis(connection_pool=self.__pool)
        data = redis.lpop(self.__config['queue'])
        self.assertIsNone(data)

    def test_empty_list_contents_internal(self) -> None:
        """
        Test if there comes nothing back when the list is empty (does the preparation work as expected?)
        """
        rqa = RedisQueueAccess(self.__config)
        redis = StrictRedis(connection_pool=rqa.create_redis_connection_pool())
        data = redis.lpop(rqa.queue)
        self.assertIsNone(data)

    def test_filled_list_contents(self) -> None:
        """
        Test if there are entries in the list (does the preparation work as expected?)
        """
        fill_items = (
            'item_1',
            'item_2',
            'item_three',
        )
        redis_filler = StrictRedis(connection_pool=self.__pool)
        for item in fill_items:
            redis_filler.lpush(self.__config['queue'], item)
        rqa = RedisQueueAccess(self.__config)
        redis_receiver = StrictRedis(connection_pool=rqa.create_redis_connection_pool())
        for item in fill_items:
            data = redis_receiver.rpop(rqa.queue)
            self.assertEqual(bytes(item, encoding='UTF-8'), data)
        self.assertIsNone(redis_receiver.rpop(rqa.queue))


class RedisQueueProducerTest(TestCase):
    """
    Test the redis queue producer
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Setup the test class
        """
        SingletonMeta.delete(ConfigurationFileFinder)
        cls.__config = ConfigurationFileFinder().find_as_json()['tts']['queues']['command']

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Clean up singleton instances of the Configuration File Finder and clear the database
        """
        StrictRedis(connection_pool=RedisQueueConfiguration(cls.__config).create_redis_connection_pool()).flushdb()
        SingletonMeta.delete(ConfigurationFileFinder)

    def setUp(self) -> None:
        """
        Flush DB before test
        """
        StrictRedis(connection_pool=RedisQueueConfiguration(self.__config).create_redis_connection_pool()).flushdb()

    def test_empty_queue(self) -> None:
        """
        See if a queue is empty by default
        """
        rqp = RedisQueueProducer(self.__config)
        redis_connection = rqp.get_connection()
        item = redis_connection.lpop(rqp.queue)
        self.assertIsNone(item)

    def test_empty_channel(self) -> None:
        """
        See if the Pub/Sub Channel is empty
        """
        rqp = RedisQueueProducer(self.__config)
        redis_connection = rqp.get_connection()
        pubsub = redis_connection.pubsub()
        pubsub.subscribe(rqp.pubsub_channel)
        for dummy in range(10):
            item = pubsub.get_message(ignore_subscribe_messages=True, timeout=.5)
            self.assertIsNone(item)
        pubsub.unsubscribe(rqp.pubsub_channel)

    def test_fire_message(self) -> None:
        """
        Test sending a message to the queue
        """
        rqp = RedisQueueProducer(self.__config)
        redis_connection = rqp.get_connection()
        pubsub = redis_connection.pubsub()
        pubsub.subscribe(rqp.pubsub_channel)
        num = rqp.fire_message('Test Message')
        self.assertEqual(1, num)
        item = pubsub.get_message(ignore_subscribe_messages=True, timeout=.25)
        self.assertIsNone(item) # the ignored message
        item = pubsub.get_message(ignore_subscribe_messages=True, timeout=.25)
        pubsub.unsubscribe(rqp.pubsub_channel)
        self.assertIsInstance(item, dict)
        self.assertIn('type', item)
        self.assertIn('data', item)
        self.assertIn('channel', item)
        self.assertEqual('message', item['type'])
        self.assertEqual(b'1', item['data'])
        self.assertEqual(bytes(rqp.pubsub_channel, encoding='UTF-8'), item['channel'])
        item = redis_connection.lpop(rqp.queue)
        self.assertEqual(b'Test Message', item)
        item = redis_connection.lpop(rqp.queue)
        self.assertIsNone(item)


class RedisQueueConsumerTest(TestCase):
    """
    Test the Redis Queue Consumer
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Setup the test class
        """
        SingletonMeta.delete(ConfigurationFileFinder)
        cls.__config = ConfigurationFileFinder().find_as_json()['tts']['queues']['command']

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Clean up singleton instances of the Configuration File Finder and clear the database
        """
        StrictRedis(connection_pool=RedisQueueConfiguration(cls.__config).create_redis_connection_pool()).flushdb()
        SingletonMeta.delete(ConfigurationFileFinder)

    def setUp(self) -> None:
        """
        Flush DB before test
        """
        StrictRedis(connection_pool=RedisQueueConfiguration(self.__config).create_redis_connection_pool()).flushdb()

    def tearDown(self) -> None:
        """
        The stopping of the receiver may take time. So we give it.
        """
        sleep(2)

    @pytest.mark.timeout(60)
    def test_receiving(self) -> None:
        """
        Test the receiving of a message
        """
        mock = Mock()
        rqc = RedisQueueConsumer(self.__config, mock)
        sleep(1)
        self.assertFalse(mock.called)
        self.assertEqual(0, mock.call_count)
        rqp = RedisQueueProducer(self.__config)
        self.assertFalse(mock.called)
        self.assertEqual(0, mock.call_count)
        receivers = rqp.fire_message('Test Message to Mock')
        self.assertFalse(mock.called)
        self.assertEqual(0, mock.call_count)
        self.assertEqual(1, receivers)
        sleep(1)
        self.assertTrue(mock.called)
        self.assertEqual(1, mock.call_count)
        call_args = mock.call_args_list[0][0][0]
        self.assertEqual(b'Test Message to Mock', call_args)
        rqc.stop()

    @pytest.mark.timeout(120)
    def test_multi_receiving(self) -> None:
        """
        Pump some messages and check the mock
        """
        mock = Mock()
        rqc = RedisQueueConsumer(self.__config, mock)
        rqp = RedisQueueProducer(self.__config)
        for message_id in range(100):
            rqp.fire_message('Message {:d}'.format(message_id))
        sleep(1)
        self.assertTrue(mock.called)
        self.assertEqual(100, mock.call_count)
        for message_id in range(100):
            expected_message = bytes('Message {:d}'.format(message_id), encoding='UTF-8')
            received = mock.call_args_list[message_id][0][0]
            self.assertEqual(expected_message, received)
        rqc.stop()
