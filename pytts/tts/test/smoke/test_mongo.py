"""
Test Presence of Mongo
"""

from unittest import TestCase
from pymongo import MongoClient
from pymongo.database import Database

from ..lib.smoke import fetch_configuration
from ...util.config import ConfigurationFileFinder
from ...util.singleton import SingletonMeta


class MongoSmokeTest(TestCase):
    """
    Simple Smoke Test for Redis Access
    """

    @classmethod
    def setUpClass(cls):
        cls.__config = fetch_configuration()
        assert 'database' in cls.__config
        database = cls.__config['database']
        assert isinstance(database, dict)
        assert 'url' in database
        url = database['url']
        assert isinstance(url, str)
        assert 'database' in database
        db = database['datavase']
        assert isinstance(db, str)
        assert 'collections' in database
        collections = database['collections']
        assert isinstance(collections, dict)
        assert 'test' in collections
        test = collections['test']
        assert isinstance(test, str)
        cls.__database_name = db
        cls.__collection_name = test
        cls.__client = MongoClient(url)

    @classmethod
    def tearDownClass(cls):
        """
        Close the redis pool
        """
        cls.__client.close()
        del cls.__client
        del cls.__collection_name
        del cls.__config
        SingletonMeta.delete(ConfigurationFileFinder)

    def test_smoke(self):
        """
        Simple Smoke Test
        """
        info = self.__client.server_info()
        self.assertIn('version', info)

    def test_collection(self):
        """
        See if I can have access to the test collection
        """
        xdb = self.__client[self.__database_name]
        self.assertIsNotNone(xdb)
        self.assertIsInstance(xdb, Database)
        self.assertEqual(self.__database_name, xdb.name)
