"""
Test basic CherryPy request
"""

from http.client import HTTPConnection
from unittest import TestCase

from ..lib.server import prepare_test, cleanup


class BasicServerTest(TestCase):
    """
    Check if there is a homepage redirect
    """

    @classmethod
    def setUpClass(cls):
        """
        Setup the server class
        """
        cls.config = dict()
        prepare_test(cls)
        cls.base_url = 'http://{:s}:{:d}/'.format(cls.config['bind_ip'], cls.config['bind_port'])

    @classmethod
    def tearDownClass(cls):
        """
        Shutdown stuff
        """
        cleanup(cls)

    def test_redirect(self):
        """
        Test if there is the desired redirect
        """
        connection = HTTPConnection(
            host=self.config['bind_ip'],
            port=self.config['bind_port']
        )
        connection.request(url='/', method='GET')
        response = connection.getresponse()
        connection.close()
        self.assertEqual(302, response.code)
        self.assertIn('Location', response.headers)
        self.assertEqual('static/index.xhtml', response.headers['Location'])
