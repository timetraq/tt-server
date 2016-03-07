"""
How to connect to a database
"""

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from ..util.config import ConfigurationFileFinder
from ..util.singleton import SingletonMeta


class DbAccess(metaclass=SingletonMeta):
    """
    Bring database access as singleton to the whole program
    """

    def __init__(self):
        """
        Prepare database connection - load the configuration
        """
        configuration = ConfigurationFileFinder().find_as_json()['tts']['database']
        pool_size = 5
        if 'pool_size' in configuration:
            pool_size = configuration['pool_size']
        max_overflow = 0
        if 'max_overflow' in configuration:
            max_overflow = configuration['max_overflow']
        if configuration['connection_url'].startswith('sqlite:'):
            self.__pool_engine = create_engine(configuration['connection_url'])
        else:
            self.__pool_engine = create_engine(configuration['connection_url'],
                                               pool_size=pool_size, max_overflow=max_overflow)

    @property
    def pool(self) -> Engine:
        """
        Get the pooled engine

        :return: The pooled engine
        :rtype: Engine
        """
        return self.__pool_engine

    def disconnect(self) -> None:
        """
        Disconnect the pool
        """
        if self.__pool_engine is not None:
            self.__pool_engine.dispose()
            del self.__pool_engine
