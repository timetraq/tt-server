"""
Test the Login API
"""

from json import loads
from http.client import HTTPConnection
from unittest import TestCase

from ..lib.server import prepare_test, cleanup


class LoginAPITest(TestCase):
    """
    Check simple Version Call
    """

    @classmethod
    def setUpClass(cls):
        """
        Setup the server class for login test
        """
        cls.config = dict()
        prepare_test(cls)

    @classmethod
    def tearDownClass(cls):
        """
        Shutdown server and clean up
        """
        cleanup(cls)

    def test_status_call(self):
        """
        Test if there is a login answer
        """
        connection = HTTPConnection(
            host=self.config['bind_ip'],
            port=self.config['bind_port']
        )
        connection.request(url='/api/v1.0/login/status', method='GET')
        response = connection.getresponse()
        self.assertEqual(200, response.code)
        self.assertIn('Content-Type', response.headers)
        self.assertEqual('application/json', response.headers['Content-Type'])
        data = response.read()
        json_data = loads(data.decode(encoding='utf-8'))
        connection.close()
        self.assertDictEqual({'status': -1}, json_data)
