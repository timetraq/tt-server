"""
Test basic CherryPy request
"""

from http.client import HTTPConnection
from unittest import TestCase

from ..lib.browser import prepare_test as browser_prepare_test, cleanup as browser_cleanup
from ..lib.server import prepare_test as server_prepare_test, cleanup as server_cleanup


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
        server_prepare_test(cls)

    @classmethod
    def tearDownClass(cls):
        """
        Shutdown stuff
        """
        server_cleanup(cls)

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


class BasicWebbrowserCheck(TestCase):
    """
    Check if there is a homepage redirect
    """

    @classmethod
    def setUpClass(cls):
        """
        Setup the server class
        """
        cls.config = dict()
        cls.webdriver = None
        browser_prepare_test(cls)
        cls.base_url = 'http://{:s}:{:d}/'.format(cls.config['bind_ip'], cls.config['bind_port'])

    @classmethod
    def tearDownClass(cls):
        """
        Shutdown stuff
        """
        browser_cleanup(cls)

    def test_get_app_page(self):
        """
        Test if a browser can see the basic Webapp Page
        """
        self.webdriver.get(self.base_url)
        expected_url = '{:s}static/index.xhtml'.format(self.base_url)
        self.assertEqual(expected_url, self.webdriver.current_url)
