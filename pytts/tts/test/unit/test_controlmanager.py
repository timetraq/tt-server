"""
Tests Collection for the Control Manager, a central component of the Timetraq Server
"""

from unittest import TestCase
from time import sleep

from redis import StrictRedis

from ...util.config import ConfigurationFileFinder
from ...util.queue.redis import RedisQueueConfiguration
from ...control.manager import ControlManager
from ...util.singleton import SingletonMeta


class ControlManagerInitializationTest(TestCase):
    """
    Test the initialization behaviour of the Control Manager
    """

    def tearDown(self) -> None:
        """
        Delete existing singleton instance of the Control Manager - clean up!
        """
        ControlManager().stop()
        sleep(2)
        SingletonMeta.delete(ControlManager)

    def test_single_init(self) -> None:
        """
        A single init via factory and a later fetch via singleton should deliver the same instance
        """
        cm1 = ControlManager.factory()
        cm2 = ControlManager()
        self.assertEqual(cm1, cm2)

    def test_single_init_multiple_call(self) -> None:
        """
        Even if the singleton is called multiple time after the factory, the object must always be the same instance
        """
        cm_master = ControlManager.factory()
        cm1 = ControlManager()
        self.assertEqual(cm_master, cm1)
        cm2 = ControlManager()
        self.assertEqual(cm_master, cm2)
        cm3 = ControlManager()
        self.assertEqual(cm_master, cm3)
        cm4 = ControlManager()
        self.assertEqual(cm_master, cm4)
        cm5 = ControlManager()
        self.assertEqual(cm_master, cm5)

    def test_double_init(self) -> None:
        """
        Calling the factory twice is invalid
        """
        ControlManager.factory()
        self.assertRaises(RuntimeError, ControlManager.factory)

    def test_init_without_factory(self) -> None:
        """
        Even without the factory, the constructor shall deliver a good instance (basically with default settings) and
        always the same instance in subsequent calls.
        """
        cm1 = ControlManager()
        cm2 = ControlManager()
        self.assertEqual(cm1, cm2)

    def test_post_configure_on_default(self) -> None:
        """
        Default created objects shall not accept a later configure
        """
        control_manager = ControlManager()
        self.assertRaises(RuntimeError, control_manager.configure)

    def test_post_configure_on_factory(self) -> None:
        """
        Factory created objects shall not accept a later configure
        """
        control_manager = ControlManager.factory()
        self.assertRaises(RuntimeError, control_manager.configure)


class ControlManagerStopTest(TestCase):
    """
    Test how the control manager main command queue can be stopped
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

    def tearDown(self) -> None:
        """
        Delete existing singleton instance of the Control Manager - clean up!
        """
        ControlManager().stop()
        sleep(2)
        SingletonMeta.delete(ControlManager)

    def test_stop_command_via_direct_call(self) -> None:
        """
        Call the stop method directly
        """
        ControlManager.factory(list())
        self.assertTrue(ControlManager().command_handler.should_run)
        ControlManager().stop()
        self.assertFalse(ControlManager().command_handler.should_run)

    def test_stop_command_via_manage_call(self) -> None:
        """
        Call the stop method via manage call
        """
        ControlManager.factory(list())
        self.assertTrue(ControlManager().command_handler.should_run)
        ControlManager().manage(b'STOP')
        self.assertFalse(ControlManager().command_handler.should_run)

    def test_stop_command_via_queue(self):
        """
        Call the stop via queue command
        """
        ControlManager.factory(list())
        self.assertTrue(ControlManager().command_handler.should_run)
        rqc = RedisQueueConfiguration(self.__config)
        redis = StrictRedis(connection_pool=rqc.create_redis_connection_pool())
        redis.rpush(rqc.queue, 'STOP')
        redis.publish('{:s}_PUBSUB_CH'.format(rqc.queue), '1')
        sleep(1)
        self.assertFalse(ControlManager().command_handler.should_run)
