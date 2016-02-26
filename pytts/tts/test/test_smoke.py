"""
This class contains some very basic smoke tests.
"""

from unittest import TestCase


class SmokeTest(TestCase):
    """
    Smoke Test collection
    """

    def test_smoke(self) -> None:
        """
        Simple test
        """
        self.assertEqual(1, 1)
