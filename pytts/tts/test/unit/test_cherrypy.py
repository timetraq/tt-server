"""
Test basic CherryPy request
"""

from http.client import HTTPConnection
from unittest import TestCase
from time import sleep

from ...control.manager import ControlManager
from ...util.config import ConfigurationFileFinder
from ...util.singleton import SingletonMeta


class BasicServerTest(TestCase):
    """
    Check if there is a homepage redirect
    """

    @classmethod
    def setUpClass(cls):
        """
        Setup the server class
        """
        cls.__ctrl_manager = ControlManager.factory()
        cls.__ctrl_manager.start()
        cls.__config = {
            'bind_ip': '127.0.0.1',
            'bind_port': 8080,
        }
        config = ConfigurationFileFinder().find_as_json()['tts']
        if 'server' in config and 'bind_ip' in config['server']:
            cls.__config['bind_ip'] = config['server']['bind_ip']
        if 'server' in config and 'bind_port' in config['server']:
            cls.__config['bind_port'] = config['server']['bind_port']
        cls.__base_url = 'http://{:s}:{:d}/'.format(cls.__config['bind_ip'], cls.__config['bind_port'])

    @classmethod
    def tearDownClass(cls):
        """
        Shutdown stuff
        """
        cls.__ctrl_manager.stop()
        sleep(5)
        SingletonMeta.delete(ConfigurationFileFinder)
        SingletonMeta.delete(ControlManager)

    def test_redirect(self):
        """
        Test if there is the desired redirect
        """
        connection = HTTPConnection(
            host=self.__config['bind_ip'],
            port=self.__config['bind_port']
        )
        connection.request(url='/', method='GET')
        response = connection.getresponse()
        connection.close()
        self.assertEqual(302, response.code)
        self.assertIn('Location', response.headers)
        self.assertEqual('static/index.html', response.headers['Location'])
