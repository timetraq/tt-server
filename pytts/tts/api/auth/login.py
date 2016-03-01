"""
Contains everything for login
"""

from flask import Flask, jsonify

from ..base.mountable import MountableAPI


class LoginStatusAPI(MountableAPI):
    """
    API for creating User Sessions
    """

    def mount(self, namespace: str, application: Flask) -> None:
        """
        Provide the mount interface

        :param namespace: The URL namespace
        :param application: The Flask Application
        """
        application.add_url_rule('{:s}/status'.format(namespace), '{:s}/status'.format(namespace),
                                 LoginStatusAPI.get_status)

    @staticmethod
    def get_status():
        """
        Show the state
        """
        return jsonify({'status': -1})
