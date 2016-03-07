"""
Base for Server Tests
"""

from http.client import HTTPConnection
from json import loads
from time import sleep
from unittest import TestCase

from ...control.manager import ControlManager
from ...util.config import ConfigurationFileFinder
from ...util.singleton import SingletonMeta


def prepare_test(cls_instance):
    """
    Setup the server class
    :param cls_instance: CLS
    """
    cls_instance.ctrl_manager = ControlManager.factory()
    cls_instance.ctrl_manager.start()
    cls_instance.config = {
        'bind_ip': '127.0.0.1',
        'bind_port': 8080,
    }
    config = ConfigurationFileFinder().find_as_json()['tts']
    if 'server' in config and 'bind_ip' in config['server']:
        cls_instance.config['bind_ip'] = config['server']['bind_ip']
    if 'server' in config and 'bind_port' in config['server']:
        cls_instance.config['bind_port'] = config['server']['bind_port']


def cleanup(cls_instance):
    """
    Shutdown stuff
    :param cls_instance: CLS
    """
    cls_instance.ctrl_manager.stop()
    sleep(5)
    SingletonMeta.delete(ConfigurationFileFinder)
    SingletonMeta.delete(ControlManager)


class ServerTestCase(TestCase):
    """
    Base Class for a Server Test
    """

    @classmethod
    def setUpClass(cls):
        """
        Setup the server class for login test
        """
        cls.config = dict()
        cls.ctrl_manager = None
        prepare_test(cls)

    @classmethod
    def tearDownClass(cls):
        """
        Shutdown server and clean up
        """
        cleanup(cls)

    def util_evaluate_json_response(self, response):
        """
        Evaluate the response for JSON

        :param response: The response to evaluate
        """
        self.assertEqual(200, response.code)
        self.assertIn('Content-Type', response.headers)
        self.assertEqual('application/json', response.headers['Content-Type'])

    def get_http_connection(self):
        """
        Get a HTTP connection with the exisiting credentials

        :return: A http connection
        :rtype: HTTPConnection
        """
        return HTTPConnection(
            host=self.config['bind_ip'],
            port=self.config['bind_port']
        )

    def get_json_response(self, url: str):
        """
        Get a JSON response

        :param url: The URL to get
        :return: The JSON respnse
        """
        connection = self.get_http_connection()
        connection.request(url=url, method='GET')
        response = connection.getresponse()
        self.util_evaluate_json_response(response)
        data = response.read()
        json_data = loads(data.decode(encoding='utf-8'))
        connection.close()
        return json_data
