"""
Tests Collection for the Control Manager, a central component of the Timetraq Server
"""

from unittest import TestCase
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
