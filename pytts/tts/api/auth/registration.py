"""
Contains everything for registration
"""

from flask import Flask, jsonify, request
from werkzeug.exceptions import BadRequest

from ..base.mountable import MountableAPI
from ...core.rules import RULE_USERNAME, RULE_TOKEN, RULE_UUID


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

    def prepare(self):
        """
        Prepare registration

        :return: JSON response
        """
        return jsonify(self.queue_dispatcher({
            '_': 'registration:prepare',
            'data': {
                'ip': request.remote_addr,
            },
        }))

    def choose_username(self):
        """
        Choose Username

        :return: JSON response
        """
        json_data = request.get_json()
        if any([
                json_data is None,
                'token' not in json_data,
                'username' not in json_data,
                'registration_key' not in json_data,
                not isinstance(json_data['token'], str),
                not isinstance(json_data['username'], str),
                not isinstance(json_data['registration_key'], str),
                not RULE_TOKEN.match(json_data['token']),
                not RULE_USERNAME.match(json_data['username']),
                not RULE_UUID.match(json_data['registration_key']),
        ]):
            raise BadRequest()
        return jsonify(self.queue_dispatcher({
            '_': 'registration:choose_username',
            'data': {
                'registration_key': json_data['registration_key'],
                'token': json_data['token'],
                'ip': request.remote_addr,
                'username': json_data['username'],
            }
        }))
