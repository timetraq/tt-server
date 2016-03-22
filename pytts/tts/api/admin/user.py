"""
Backend for managing users
"""

from flask import Flask, jsonify, request
from redis import StrictRedis
from werkzeug.exceptions import BadRequest

from ..base.mountable import MountableAPI
from ...core.rules import RULE_TOKEN
from ...util.config import ConfigurationFileFinder
from ...util.redis import RedisConfiguration


class UserManagementAPI(MountableAPI):
    """
    User Management API implementation
    """

    api_redis = RedisConfiguration(
        configuration=ConfigurationFileFinder().find_as_json()['tts']['queues']['api']
    )

    api_pool = api_redis.create_redis_connection_pool()

    def __init__(self):
        """
        Prepare dispatching queue
        """
        super(UserManagementAPI, self).__init__()

    def mount(self, namespace: str, application: Flask) -> None:
        """
        Provide the mount interface

        :param namespace: The URL namespace
        :param application: The Flask Application
        """
        enable_user_endpoint = '{:s}/enable_user'.format(namespace)
        application.add_url_rule(enable_user_endpoint, enable_user_endpoint, self.enable_user, methods=('POST',))
        disable_user_endpoint = '{:s}/disable_user'.format(namespace)
        application.add_url_rule(disable_user_endpoint, disable_user_endpoint, self.disable_user, methods=('POST',))
        set_password_endpoint = '{:s}/set_password'.format(namespace)
        application.add_url_rule(set_password_endpoint, set_password_endpoint, self.set_password, methods=('POST',))

    def __admin_handler(self, endpoint: bytes):
        """
        Handle Admin Request

        :param bytes endpoint: Endpoint (in bytes!)
        :return: jsonified answer data
        """
        json_data = request.get_json()
        if json_data is None:
            raise BadRequest()
        if 'admin_token' not in json_data:
            raise BadRequest()
        admin_token = json_data['admin_token']
        if not isinstance(admin_token, str):
            raise BadRequest()
        if not RULE_TOKEN.match(admin_token):
            raise BadRequest()
        redis = StrictRedis(connection_pool=self.api_pool)
        ep_key = 'ADMIN_TOKEN:{:s}'.format(admin_token)
        should_endpoint = redis.get(ep_key)
        if should_endpoint is None:
            raise BadRequest()
        redis.delete(ep_key)
        if should_endpoint != endpoint:
            raise BadRequest()
        if 'data' not in json_data:
            raise BadRequest()
        data = json_data['data']
        if not isinstance(data, dict):
            raise BadRequest()
        return jsonify(self.queue_dispatcher({
            '_': 'admin:{:s}'.format(endpoint.decode('utf-8')),
            'data': data,
        }))

    def enable_user(self):
        """
        Enable the user

        :return: JSON response
        """
        return self.__admin_handler(b'enable_user')

    def disable_user(self):
        """
        Disable the user

        :return: JSON response
        """
        return self.__admin_handler(b'disable_user')

    def set_password(self):
        """
        Set a user's password

        :return: JSON response
        """
        return self.__admin_handler(b'set_password')
