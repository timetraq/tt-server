"""
Classes for configuration
"""

from json import load
import re
from os import path, environ
import sys
from .singleton import SingletonMeta


class ConfigurationFileFinder(object, metaclass=SingletonMeta):
    """
    Provide a finder for the configuration file '``pytts.json``'
    """

    @staticmethod
    def get_from_default() -> str:
        """
        Try to file at the standard location

        :return: The filename including the complete path or ``None``, if not found
        :rtype: str
        """
        file = '/etc/pytts/tt-server.json'
        if not path.exists(file) or not path.isfile(file):
            return None
        return file

    @staticmethod
    def get_from_environment_variable() -> str:
        """
        Try to file at the a location where a environment variable points to.

        The environment variable is ``PYTTS_CONFIGURATION_FILE``

        If the value of the environment variable changes between two calls, the new value will be used.

        :return: The filename including the complete path or ``None``, if not found
        :rtype: str
        :raises: FileNotFoundError: when variable is specified, but file not found
        """
        if 'PYTTS_CONFIGURATION_FILE' not in environ:
            return None
        file = environ['PYTTS_CONFIGURATION_FILE']
        if not path.exists(file):
            raise FileNotFoundError
        if not path.isfile(file):
            raise FileNotFoundError
        return file

    @staticmethod
    def get_from_cmd_line_arg() -> str:
        """
        Try to file at the a location where a command line argument points to.

        The argument is ``--config=<file>``.

        :return: The filename including the complete path or ``None``, if not found
        :rtype: str
        :raises: FileNotFoundError: when command line argument is specified, but file not found
        """
        pattern = re.compile(r'^\-\-(?P<key>[a-zA-Z][a-zA-Z_0-9]*)=["]?(?P<value>[^"]+)["]?$', re.UNICODE)
        for arg in sys.argv:
            match = pattern.match(arg)
            if not match:
                continue
            key = match.group('key')
            if key != 'config':
                continue
            file = match.group('value')
            if not path.exists(file):
                raise FileNotFoundError
            if not path.isfile(file):
                raise FileNotFoundError
            return file
        return None

    def __init__(self):
        self.__finders = (
            ConfigurationFileFinder.get_from_cmd_line_arg,
            ConfigurationFileFinder.get_from_environment_variable,
            ConfigurationFileFinder.get_from_default,
        )

    def find(self) -> str:
        """
        Find the configuration file

        :return: The filename including the complete path or ``None``, if not found
        :rtype: str
        :raises FileNotFoundError: When no configuration file was found
        """
        for finder_function in self.__finders:
            result = finder_function()
            if result is not None:
                return result
        raise FileNotFoundError('No configuration file found')

    def find_as_json(self) -> dict:
        """
        Find the file and parse the JSON

        :return: An object containing the configuration
        :rtype: dict
        :raises FileNotFoundError: When no configuration file was found
        :raises JSONDecodeError: When the JSON data is invalid
        :raises IOError: When something reading the file goes wrong
        """
        file = self.find()
        with open(file, 'r') as file_pointer:
            data = load(file_pointer)
        return data
