"""
Test the Login API
"""

from ..lib.server import ServerTestCase


class LoginAPITest(ServerTestCase):
    """
    Check simple Version Call
    """

    def test_status_call(self):
        """
        Test if there is a login answer
        """
        json_data = self.get_json_response('/api/v1.0/login/status')
        self.assertDictEqual({'status': -1}, json_data)
