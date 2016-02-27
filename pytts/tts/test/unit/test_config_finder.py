# pylint: disable=too-many-public-methods
"""
Test the central config file finder
"""

import os
import sys
from json import JSONDecodeError
from unittest import TestCase
from ...util.config import ConfigurationFileFinder
from ...util.singleton import SingletonMeta


class ConfigFinderTest(TestCase):
    """
    Make sure the configuration finder is a singleton and works as expected in an environment

    DANGER: The test requires that there is no configuration file at the default location!
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Save the current environment variable, save the command line arguments
        """
        try:
            cls.__saved_environment_variable = str(os.environ['PYTTS_CONFIGURATION_FILE'])
        except KeyError:
            cls.__saved_environment_variable = None
        cls.__command_line_arguments = sys.argv.copy()

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Store the saved environment variable back, write the command line arguments back
        """
        if cls.__saved_environment_variable is None:
            try:
                del os.environ['PYTTS_CONFIGURATION_FILE']
            except KeyError:
                pass
        else:
            os.environ['PYTTS_CONFIGURATION_FILE'] = cls.__saved_environment_variable
        sys.argv = cls.__command_line_arguments

    def tearDown(self) -> None:
        """
        Remove the singleton instance
        """
        SingletonMeta.delete(ConfigurationFileFinder)

    def setUp(self):
        """
        Provide a clean environment for each test
        """
        try:
            del os.environ['PYTTS_CONFIGURATION_FILE']
        except KeyError:
            pass
        sys.argv = list()

    def test_only_one_instance(self) -> None:
        """
        Check that on subsequent calls the same instance is always returned
        """
        cff1 = ConfigurationFileFinder()
        cff2 = ConfigurationFileFinder()
        self.assertEqual(cff1, cff2)

    def test_only_one_instance_under_changed_config(self) -> None:
        """
        Add an environment variable during test
        """
        cff1 = ConfigurationFileFinder()
        os.environ['PYTTS_CONFIGURATION_FILE'] = 'test.json'
        cff2 = ConfigurationFileFinder()
        self.assertEqual(cff1, cff2)

    def test_get_default(self) -> None:
        """
        In a clean environment, without command line arguments and environment variables, the default should be
        returned. Since it does not exist in our testing environment, a ``FileNotFoundError`` is expected.
        """
        config_file_finder = ConfigurationFileFinder()
        self.assertRaises(FileNotFoundError, config_file_finder.find)

    def test_get_default_json(self) -> None:
        """
        In a clean environment, without command line arguments and environment variables, the default should be
        returned. Since it does not exist in our testing environment, a ``FileNotFoundError`` is expected, even if
        we ask for a parsed JSON object.
        """
        config_file_finder = ConfigurationFileFinder()
        self.assertRaises(FileNotFoundError, config_file_finder.find_as_json)

    @staticmethod
    def utility_mock_finder(file: str) -> str:
        """
        Find a file in the mock-files folder

        :param file: File to find in the mock files
        :return: full file path
        :rtype: str
        """
        mock_file = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            '..',
            'mock',
            'mock-files',
            file
        ))
        if not os.path.exists(mock_file) or not os.path.isfile(mock_file):
            raise FileNotFoundError('Mock File not found')
        return mock_file

    def __utility_findonly_env_helper(self, filename: str) -> None:
        """
        Execute a test with the environment variable - only try to find the file, not check it

        :param filename: Filename from mock-files folder
        """
        file = ConfigFinderTest.utility_mock_finder(filename)
        os.environ['PYTTS_CONFIGURATION_FILE'] = file
        config_file_finder = ConfigurationFileFinder()
        found = config_file_finder.find()
        self.assertEqual(file, found)

    def __utility_findonly_cmd_helper(self, filename: str) -> None:
        """
        Execute a test with the command line argument - only try to find the file, not check it

        :param filename: Filename from mock-files folder
        """
        file = ConfigFinderTest.utility_mock_finder(filename)
        sys.argv.append(
            '--config="{:s}"'.format(file)
        )
        config_file_finder = ConfigurationFileFinder()
        found = config_file_finder.find()
        self.assertEqual(file, found)

    def __utility_find_and_parse_env_helper(self, filename: str, expect_parse_exception: bool) -> None:
        """
        Find and parse a file from the environment

        :param filename: Filename from mock-files-folder
        :param expect_parse_exception: Should a error be raised?
        """
        file = ConfigFinderTest.utility_mock_finder(filename)
        os.environ['PYTTS_CONFIGURATION_FILE'] = file
        config_file_finder = ConfigurationFileFinder()
        if expect_parse_exception:
            self.assertRaises(JSONDecodeError, config_file_finder.find_as_json)
        else:
            data = config_file_finder.find_as_json()
            self.assertIsInstance(data, dict)

    def __utility_find_and_parse_cmd_helper(self, filename: str, expect_parse_exception: bool) -> None:
        """
        Find and parse a file from the command line arguments

        :param filename: Filename from mock-files-folder
        :param expect_parse_exception: Should a error be raised?
        """
        file = ConfigFinderTest.utility_mock_finder(filename)
        sys.argv.append(
            '--config="{:s}"'.format(file)
        )
        config_file_finder = ConfigurationFileFinder()
        if expect_parse_exception:
            self.assertRaises(JSONDecodeError, config_file_finder.find_as_json)
        else:
            data = config_file_finder.find_as_json()
            self.assertIsInstance(data, dict)

    def test_invalid_config_file_findonly_by_env(self):
        """
        Try to simply find the file, no JSON evaluation
        """
        self.__utility_findonly_env_helper('invalid-config-file.json')

    def test_empty_config_file_findonly_by_env(self):
        """
        Try to simply find the file, no JSON evaluation
        """
        self.__utility_findonly_env_helper('empty-config-file.json')

    def test_empty_jsonconfig_file_findonly_by_env(self):
        """
        Try to simply find the file, no JSON evaluation
        """
        self.__utility_findonly_env_helper('empty-json-config-file.json')

    def test_invalid_config_file_findonly_by_cmd(self):
        """
        Try to simply find the file, no JSON evaluation
        """
        self.__utility_findonly_cmd_helper('invalid-config-file.json')

    def test_empty_config_file_findonly_by_cmd(self):
        """
        Try to simply find the file, no JSON evaluation
        """
        self.__utility_findonly_cmd_helper('empty-config-file.json')

    def test_empty_jsonconfig_file_findonly_by_cmd(self):
        """
        Try to simply find the file, no JSON evaluation
        """
        self.__utility_findonly_cmd_helper('empty-json-config-file.json')

    def test_invalid_config_file_findparse_by_env(self):
        """
        Try and parse
        """
        self.__utility_find_and_parse_env_helper('invalid-config-file.json', True)

    def test_empty_config_file_findparse_by_env(self):
        """
        Try and parse
        """
        self.__utility_find_and_parse_env_helper('empty-config-file.json', True)

    def test_empty_jsonconfig_file_findparse_by_env(self):
        """
        Try and parse
        """
        self.__utility_find_and_parse_env_helper('empty-json-config-file.json', False)

    def test_invalid_config_file_findparse_by_cmd(self):
        """
        Try and parse
        """
        self.__utility_find_and_parse_cmd_helper('invalid-config-file.json', True)

    def test_empty_config_file_findparse_by_cmd(self):
        """
        Try and parse
        """
        self.__utility_find_and_parse_cmd_helper('empty-config-file.json', True)

    def test_empty_jsonconfig_file_findparse_by_cmd(self):
        """
        Try and parse
        """
        self.__utility_find_and_parse_cmd_helper('empty-json-config-file.json', False)

    def test_find_exception_on_set_cmd(self):
        """
        Test if an ``FileNotFoundError`` is raised when the command line argument is set, but the file is not found
        """
        sys.argv.append('--config="/does/not/exist/config.json"')
        config_file_finder = ConfigurationFileFinder()
        self.assertRaises(FileNotFoundError, config_file_finder.find)

    def test_find_exception_on_set_env(self):
        """
        Test if an ``FileNotFoundError`` is raised when the environment variable is set, but the file is not found
        """
        os.environ['PYTTS_CONFIGURATION_FILE'] = '/does/not/exist/config.json'
        config_file_finder = ConfigurationFileFinder()
        self.assertRaises(FileNotFoundError, config_file_finder.find)

    def test_findparse_exception_on_set_cmd(self):
        """
        Test if an ``FileNotFoundError`` is raised when the command line argument is set, but the file is not found
        """
        sys.argv.append('--config="/does/not/exist/config.json"')
        config_file_finder = ConfigurationFileFinder()
        self.assertRaises(FileNotFoundError, config_file_finder.find_as_json)

    def test_findparse_exception_on_set_env(self):
        """
        Test if an ``FileNotFoundError`` is raised when the environment variable is set, but the file is not found
        """
        os.environ['PYTTS_CONFIGURATION_FILE'] = '/does/not/exist/config.json'
        config_file_finder = ConfigurationFileFinder()
        self.assertRaises(FileNotFoundError, config_file_finder.find_as_json)

    def test_find_exception_on_existing_dir_on_set_cmd(self):
        """
        Test if an ``FileNotFoundError`` is raised when the command line argument is set, but the file is not found
        """
        file = os.path.abspath(os.path.join(
            os.path.dirname(ConfigFinderTest.utility_mock_finder('empty-config-file.json')),
            'does-not-exist.json'
        ))
        sys.argv.append('--config="{:s}"'.format(file))
        config_file_finder = ConfigurationFileFinder()
        self.assertRaises(FileNotFoundError, config_file_finder.find)

    def test_find_exception_on_existing_dir_on_set_env(self):
        """
        Test if an ``FileNotFoundError`` is raised when the environment variable is set, but the file is not found
        """
        file = os.path.abspath(os.path.join(
            os.path.dirname(ConfigFinderTest.utility_mock_finder('empty-config-file.json')),
            'does-not-exist.json'
        ))
        os.environ['PYTTS_CONFIGURATION_FILE'] = file
        config_file_finder = ConfigurationFileFinder()
        self.assertRaises(FileNotFoundError, config_file_finder.find)

    def test_findparse_exception_on_existing_dir_on_set_cmd(self):
        """
        Test if an ``FileNotFoundError`` is raised when the command line argument is set, but the file is not found
        """
        file = os.path.abspath(os.path.join(
            os.path.dirname(ConfigFinderTest.utility_mock_finder('empty-config-file.json')),
            'does-not-exist.json'
        ))
        sys.argv.append('--config="{:s}"'.format(file))
        config_file_finder = ConfigurationFileFinder()
        self.assertRaises(FileNotFoundError, config_file_finder.find_as_json)

    def test_findparse_exception_on_existing_dir_on_set_env(self):
        """
        Test if an ``FileNotFoundError`` is raised when the environment variable is set, but the file is not found
        """
        file = os.path.abspath(os.path.join(
            os.path.dirname(ConfigFinderTest.utility_mock_finder('empty-config-file.json')),
            'does-not-exist.json'
        ))
        os.environ['PYTTS_CONFIGURATION_FILE'] = file
        config_file_finder = ConfigurationFileFinder()
        self.assertRaises(FileNotFoundError, config_file_finder.find_as_json)

    def test_find_exception_on_dir_on_set_cmd(self):
        """
        Test if an ``FileNotFoundError`` is raised when the command line argument is set, but the file is not found
        """
        file = os.path.abspath(os.path.join(
            os.path.dirname(ConfigFinderTest.utility_mock_finder('empty-config-file.json'))
        ))
        sys.argv.append('--config="{:s}"'.format(file))
        config_file_finder = ConfigurationFileFinder()
        self.assertRaises(FileNotFoundError, config_file_finder.find)

    def test_find_exception_on_dir_on_set_env(self):
        """
        Test if an ``FileNotFoundError`` is raised when the environment variable is set, but the file is not found
        """
        file = os.path.abspath(os.path.join(
            os.path.dirname(ConfigFinderTest.utility_mock_finder('empty-config-file.json'))
        ))
        os.environ['PYTTS_CONFIGURATION_FILE'] = file
        config_file_finder = ConfigurationFileFinder()
        self.assertRaises(FileNotFoundError, config_file_finder.find)

    def test_findparse_exception_on_dir_on_set_cmd(self):
        """
        Test if an ``FileNotFoundError`` is raised when the command line argument is set, but the file is not found
        """
        file = os.path.abspath(os.path.join(
            os.path.dirname(ConfigFinderTest.utility_mock_finder('empty-config-file.json'))
        ))
        sys.argv.append('--config="{:s}"'.format(file))
        config_file_finder = ConfigurationFileFinder()
        self.assertRaises(FileNotFoundError, config_file_finder.find_as_json)

    def test_findparse_exception_on_dir_on_set_env(self):
        """
        Test if an ``FileNotFoundError`` is raised when the environment variable is set, but the file is not found
        """
        file = os.path.abspath(os.path.join(
            os.path.dirname(ConfigFinderTest.utility_mock_finder('empty-config-file.json'))
        ))
        os.environ['PYTTS_CONFIGURATION_FILE'] = file
        config_file_finder = ConfigurationFileFinder()
        self.assertRaises(FileNotFoundError, config_file_finder.find_as_json)

    def test_with_multiple_cmd_arguments(self):
        """
        Test if an ``FileNotFoundError`` is raised when the environment variable is set, but the file is not found
        """
        sys.argv.append('--configx="a"')
        sys.argv.append('--configy="a"')
        sys.argv.append('--configz="a"')
        sys.argv.append('-config="a"')
        config_file_finder = ConfigurationFileFinder()
        self.assertRaises(FileNotFoundError, config_file_finder.find_as_json)
