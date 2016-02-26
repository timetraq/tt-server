"""
Test the functionality of the singleton metaclass system with mocked classes
"""

from unittest import TestCase
from ...util.singleton import SingletonMeta
from ..mock.classes import MockClassOneSingleton, MockClassTwoSingleton


class SingletonTest(TestCase):
    """
    We heavily rely on the singleton mechanism. These are some basic tests.
    """

    def tearDown(self) -> None:
        """
        Clean up instances
        """
        SingletonMeta.delete(MockClassOneSingleton)
        SingletonMeta.delete(MockClassTwoSingleton)

    def test_retrieval_simple_one(self) -> None:
        """
        Simple singleton, single one, with MockClassOneSingleton
        """
        mock_one = MockClassOneSingleton()
        mock_two = MockClassOneSingleton()
        self.assertEqual(mock_one, mock_two)
        self.assertEqual(mock_one.uuid, mock_two.uuid)

    def test_retrieval_simple_two(self) -> None:
        """
        Simple singleton, single one, with MockClassTwoSingleton
        """
        mock_one = MockClassTwoSingleton()
        mock_two = MockClassTwoSingleton()
        self.assertEqual(mock_one, mock_two)
        self.assertEqual(mock_one.uuid, mock_two.uuid)

    def test_no_retrieval(self) -> None:
        """
        No predefined singleton
        """
        mock_one = MockClassOneSingleton()
        mock_two = MockClassTwoSingleton()
        self.assertNotEqual(mock_one, mock_two)
        self.assertNotEqual(mock_one.uuid, mock_two.uuid)

    def test_singleton_deletion(self) -> None:
        """
        Delete a singleton
        """
        mock_one = MockClassOneSingleton()
        SingletonMeta.delete(MockClassOneSingleton)
        mock_two = MockClassOneSingleton()
        self.assertNotEqual(mock_one, mock_two)
        self.assertNotEqual(mock_one.uuid, mock_two.uuid)

    def test_singleton_unique_deletion(self) -> None:
        """
        Singleton deletion shall be strictly unique
        """
        mock_one_one = MockClassOneSingleton()
        mock_one_two = MockClassOneSingleton()
        mock_two_one = MockClassTwoSingleton()
        SingletonMeta.delete(MockClassTwoSingleton)
        mock_two_two = MockClassTwoSingleton()
        self.assertEqual(mock_one_one, mock_one_two)
        self.assertEqual(mock_one_one.uuid, mock_one_two.uuid)
        self.assertNotEqual(mock_two_one, mock_two_two)
        self.assertNotEqual(mock_two_one.uuid, mock_two_two.uuid)
