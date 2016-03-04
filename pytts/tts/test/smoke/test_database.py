"""
Test if the configured databases are available
"""

from os import path
from unittest import TestCase

from sqlalchemy import create_engine
from ...util.config import ConfigurationFileFinder
from ...util.singleton import SingletonMeta


class DatabaseSmokeTest(TestCase):
    """
    Test the database connection
    """

    @staticmethod
    def util_get_database_connect_url(database_key: str) -> str:
        """
        Get the database URL from the configuration

        :param database_key: The key of the database in the configuration
        :return: The parsed database URL
        :rtype: str
        """
        config_dir = path.dirname(ConfigurationFileFinder().find())
        config = ConfigurationFileFinder().find_as_json()
        config_url = config['tts'][database_key]['connection_url']
        return config_url.replace('{{CONFIG_DIR}}', config_dir)

    @classmethod
    def setUpClass(cls):
        """
        Build an engine for the Main Database
        """
        cls.__engine = create_engine(DatabaseSmokeTest.util_get_database_connect_url('database'))

    @classmethod
    def tearDownClass(cls):
        """
        Clean up Singletons
        """
        SingletonMeta.delete(ConfigurationFileFinder)

    def test_smoke(self):
        """
        Test Main Database
        """
        print(self.__engine)
        self.__engine.connect()
        self.__engine.dispose()


class TestDatabaseSmokeTest(DatabaseSmokeTest):
    """
    Test if the Test Database is there
    """

    @classmethod
    def setUpClass(cls):
        """
        Build an engine for the Test Database
        """
        cls.__engine = create_engine(DatabaseSmokeTest.util_get_database_connect_url('testDatabase'))
