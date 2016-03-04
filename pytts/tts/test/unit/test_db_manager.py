"""
Tests for the database manager
"""

from unittest import TestCase

from sqlalchemy.engine import Engine

from ...db.manager import DbAccess
from ...util.config import ConfigurationFileFinder
from ...util.singleton import SingletonMeta


class DbManagerBaseTest(TestCase):
    """
    Basic tests
    """

    @classmethod
    def tearDownClass(cls):
        """
        Clean up Config File finder
        """
        DbAccess().disconnect()
        SingletonMeta(ConfigurationFileFinder)

    def tearDown(self):
        """
        Clean up DbAccess
        """
        DbAccess().disconnect()
        SingletonMeta.delete(DbAccess)

    def test_engine(self):
        """
        Test if there is an engine present
        """
        engine = DbAccess().pool
        self.assertIsNotNone(engine)
        self.assertIsInstance(engine, Engine)
