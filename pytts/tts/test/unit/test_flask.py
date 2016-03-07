"""
Test basic flask
"""

from ..lib.server import ServerTestCase


class BasicFlaskResponseTest(ServerTestCase):
    """
    Check simple Version Call
    """

    def test_version_call(self):
        """
        Test if there is a version answer
        """
        json_data = self.get_json_response('/api/version')
        self.assertDictEqual({'version': '1.0'}, json_data)
