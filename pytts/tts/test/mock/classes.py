"""
This module contains some simple Mock classes for easy testing
"""

from uuid import uuid4
from ...util.singleton import SingletonMeta


class MockClassOne(object):
    """
    Simple class with random content
    """

    def __init__(self):
        self.__uuid = uuid4()

    @property
    def uuid(self) -> str:
        """
        Tell about the random uuid
        :return: The random uuid
        :rtype: str
        """
        return str(self.__uuid)

    def method_one(self) -> None:
        """
        Dummy method
        """
        pass


class MockClassTwo(object):
    """
    Simple class with random content
    """

    def __init__(self):
        self.__uuid = uuid4()

    @property
    def uuid(self) -> str:
        """
        Tell about the random uuid
        :return: The random uuid
        :rtype: str
        """
        return str(self.__uuid)

    def method_two(self) -> None:
        """
        Dummy method
        """
        pass


class MockClassOneSingleton(MockClassOne, metaclass=SingletonMeta):
    """
    Singleton Version of MockClassOne
    """

    def method_one_singleton(self) -> None:
        """
        Dummy method
        """
        pass


class MockClassTwoSingleton(MockClassTwo, metaclass=SingletonMeta):
    """
    Singleton Version of MockClassTwo
    """

    def method_two_singleton(self) -> None:
        """
        Dummy method
        """
        pass
