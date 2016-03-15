"""
Contains everything for registration
"""

from flask import Flask, jsonify, request
from werkzeug.exceptions import BadRequest

from ..base.mountable import MountableAPI
from ...core.rules import RULE_USERNAME, RULE_TOKEN, RULE_UUID, RULE_PASSWORD


class RegistrationAPI(MountableAPI):
    """
    API for Registration
    """

    def __init__(self):
        """
        Prepare dispatching queue
        """
        super(RegistrationAPI, self).__init__()

    def mount(self, namespace: str, application: Flask):
        """
        Mount Registration API

        :param namespace: Namespace
        :param application: Application
        """
        prepare_endpoint = '{:s}/prepare'.format(namespace)
        application.add_url_rule(prepare_endpoint, prepare_endpoint, self.prepare, methods=('GET',))
        choose_username_endpoint = '{:s}/choose_username'.format(namespace)
        application.add_url_rule(choose_username_endpoint, choose_username_endpoint,
                                 self.choose_username, methods=('POST',))
        set_password_endpoint = '{:s}/set_password'.format(namespace)
        application.add_url_rule(set_password_endpoint, set_password_endpoint,
                                 self.set_password, methods=('POST',))

    def prepare(self):
        """
        Prepare registration

        :return: JSON response
        """
        return jsonify(self.queue_dispatcher({
            '_': 'registration:prepare',
            'data': {
                'ip': MountableAPI.get_ip(request),
            },
        }))

    def choose_username(self):
        """
        Choose Username

        :return: JSON response
        """
        json_data = request.get_json()
        if json_data is None \
            or 'token' not in json_data \
            or 'username' not in json_data \
            or 'registration_key' not in json_data \
            or not isinstance(json_data['token'], str) \
            or not isinstance(json_data['username'], str) \
            or not isinstance(json_data['registration_key'], str) \
            or not RULE_TOKEN.match(json_data['token']) \
            or not RULE_USERNAME.match(json_data['username']) \
                or not RULE_UUID.match(json_data['registration_key']):
            raise BadRequest()
        return jsonify(self.queue_dispatcher({
            '_': 'registration:choose_username',
            'data': {
                'registration_key': json_data['registration_key'],
                'token': json_data['token'],
                'ip': MountableAPI.get_ip(request),
                'username': json_data['username'],
            }
        }))

    def set_password(self):
        """
        Set a password for the newly created user

        :return: JSON response
        """
        json_data = request.get_json()
        if json_data is None \
            or 'token' not in json_data \
            or 'registration_key' not in json_data \
            or 'password' not in json_data \
            or not isinstance(json_data['token'], str) \
            or not isinstance(json_data['registration_key'], str) \
            or not isinstance(json_data['password'], str) \
            or not RULE_TOKEN.match(json_data['token']) \
            or not RULE_UUID.match(json_data['registration_key']) \
                or not RULE_PASSWORD.match(json_data['password']):
            raise BadRequest()
        return jsonify(self.queue_dispatcher({
            '_': 'registration:set_password',
            'data': {
                'registration_key': json_data['registration_key'],
                'token': json_data['token'],
                'ip': MountableAPI.get_ip(request),
                'password': json_data['password']
            }
        }))
