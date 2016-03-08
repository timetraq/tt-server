"""
Contains everything for login
"""

from flask import Flask, jsonify, request
from werkzeug.exceptions import BadRequest

from ..base.mountable import MountableAPI
from ...core.rules import RULE_USERNAME, RULE_PASSWORD, RULE_TOKEN


class LoginAPI(MountableAPI):
    """
    API for creating and managing User Sessions
    """

    def __init__(self):
        """
        Prepare dispatching queue
        """
        super(LoginAPI, self).__init__()

    def mount(self, namespace: str, application: Flask) -> None:
        """
        Provide the mount interface

        :param namespace: The URL namespace
        :param application: The Flask Application
        """
        status_endpoint = '{:s}/status'.format(namespace)
        application.add_url_rule(status_endpoint, status_endpoint, self.get_status, methods=('POST',))
        authenticate_endpoint = '{:s}/authenticate'.format(namespace)
        application.add_url_rule(authenticate_endpoint, authenticate_endpoint, self.authenticate, methods=('POST',))

    def authenticate(self):
        """
        Authenticate a user

        :return: JSON response
        """
        json_data = request.get_json()
        if json_data is None:
            raise BadRequest()
        if 'username' not in json_data or 'password' not in json_data:
            raise BadRequest()
        if not isinstance(json_data['username'], str) or not isinstance(json_data['password'], str):
            raise BadRequest()
        username = json_data['username']
        password = json_data['password']
        if not RULE_USERNAME.match(username):
            raise BadRequest()
        if not RULE_PASSWORD.match(password):
            raise BadRequest()
        return jsonify(self.queue_dispatcher({
            '_': 'login:authenticate',
            'data': {
                'username': username,
                'password': password,
            },
        }))

    def get_status(self):
        """
        Show the state

        :return: JSON response
        """
        json_data = request.get_json()
        if json_data is None:
            raise BadRequest()
        if 'token' not in json_data:
            raise BadRequest()
        if not isinstance(json_data['token'], str):
            raise BadRequest()
        token = json_data['token']
        if not RULE_TOKEN.match(token):
            raise BadRequest()
        return jsonify(self.queue_dispatcher({
            '_': 'login:status',
            'data': {
                'token': token,
            },
        }))
