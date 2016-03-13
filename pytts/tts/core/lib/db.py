"""
Base for using the Database(s)
"""

from pymongo import MongoClient

from ...util.config import ConfigurationFileFinder


class MongoConnectivity(object):
    """
    Prepare everything for Mongo Usage
    """

    def __init__(self):
        """
        Provide a basic mongo db client connection
        """
        self._configuration = ConfigurationFileFinder().find_as_json()['tts']['database']
        self.__database = self._configuration['database']
        self.__mongo_client = MongoClient(self._configuration['url'])
        self._mongo_db = self.__mongo_client[self.__database]

    def close(self):
        """
        Close the client and all connections with it
        """
        self.__mongo_client.close()

    def __del__(self):
        """
        On deletion, close all Client connections before
        """
        self.close()


class TestDatabaseConnectivity(MongoConnectivity):
    """
    Connection to the Test Database
    """

    def __init__(self):
        """
        Prepare DB connection for test
        """
        super(TestDatabaseConnectivity, self).__init__()
        self.__test_collection = self._mongo_db[self._configuration['collections']['test']]

    @property
    def collection(self):
        return self.__test_collection


class UserDatabaseConnectivity(MongoConnectivity):
    """
    Connection to the User Database
    """

    def __init__(self):
        """
        Prepare DB connection for timetraq-users
        """
        super(UserDatabaseConnectivity, self).__init__()
        self.__user_collection = self._mongo_db[self._configuration['collections']['users']]

    @property
    def collection(self):
        return self.__user_collection
