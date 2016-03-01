"""
Test the base class for the API
"""

from unittest import TestCase
from unittest.mock import Mock

from ...api.base.mountable import MountableAPI


class APIBaseClassTest(TestCase):
    """
    Simple test for the API Base Class
    """

    def test_mountable_api_base_class(self):
        """
        An error should occur when someone calls this
        """
        mock = Mock()
        mapi = MountableAPI()
        self.assertRaises(NotImplementedError, mapi.mount, 'namespace', mock)
        self.assertFalse(mock.called)
