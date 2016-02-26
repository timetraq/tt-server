"""
This class contains some very basic smoke tests for the pytts launcher
"""

from unittest import TestCase
from types import ModuleType


class PyttsSmokeTest(TestCase):
    """
    Smoke Test collection
    """

    def test_smoke(self) -> None:
        """
        Simple Import test
        """
        from ...pytts import manager
        self.assertIsInstance(manager, ModuleType)
