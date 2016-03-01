"""
Base Class for a mountable API
"""

from flask import Flask


class MountableAPI(object):
    """
    Provide a basic class for supporting mountable API endpoints
    """

    def mount(self, namespace: str, application: Flask) -> None:
        """

        :param namespace: The mount point namespace
        :param application: The flask application
        :raises NotImplementedError: when not implemented
        """
        raise NotImplementedError
