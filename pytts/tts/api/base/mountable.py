"""
Base Class for a mountable API
"""

from flask import Flask


class MountableAPI(object):
    """
    Provide a basic class for supporting mountable API endpoints
    """

    def mount(self, namespace: str, application: Flask) -> None:
        raise NotImplementedError
