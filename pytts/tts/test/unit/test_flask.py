"""
Test basic flask
"""

from json import loads
from http.client import HTTPConnection
from unittest import TestCase

from ..lib.server import prepare_test, cleanup


class BasicFlaskResponseTest(TestCase):
    """
    Check simple Version Call
    """

    @classmethod
    def setUpClass(cls):
        """
        Setup the server class
        """
        cls.config = dict()
        prepare_test(cls)

    @classmethod
    def tearDownClass(cls):
        """
        Shutdown stuff
        """
        cleanup(cls)

    def test_version_call(self):
        """
        Test if there is a version answer
        """
        connection = HTTPConnection(
            host=self.config['bind_ip'],
            port=self.config['bind_port']
        )
        connection.request(url='/api/version', method='GET')
        response = connection.getresponse()
        self.assertEqual(200, response.code)
        self.assertIn('Content-Type', response.headers)
        self.assertEqual('application/json', response.headers['Content-Type'])
        data = response.read()
        json_data = loads(data.decode(encoding='utf-8'))
        connection.close()
        self.assertDictEqual({'version': '1.0'}, json_data)
