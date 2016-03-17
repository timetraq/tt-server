"""
Flask API entry point
"""

from blackred import BlackRed
from flask import Flask, jsonify, request
from werkzeug.exceptions import Unauthorized, BadRequest, MethodNotAllowed

from .admin.user import UserManagementAPI
from .auth.registration import RegistrationAPI
from .auth.login import LoginAPI


__version__ = '1.0'

REST_APPLICATION = Flask(__name__)
BLACKRED = BlackRed()


@REST_APPLICATION.route('/version', methods=('GET',))
def get_version():
    """
    Simply return the version of the API as JSON data

    :return: JSONified version
    """
    return jsonify({'version': __version__})


@REST_APPLICATION.before_request
def check_blackred():
    """
    Check if the IP address of the remote user is on the blacklist
    :raises Unauthorized: When the remote user is blocked
    """
    remote_addr = request.remote_addr
    if BLACKRED.is_blocked(remote_addr):
        raise Unauthorized()


@REST_APPLICATION.before_request
def check_request():
    """
    Check if the request is a JSON one on POST and uses only allowed methods
    :raises BadRequest: When post contains no JSON
    :raises MethodNotAllowed: When not GET or POST is used
    """
    if not any([request.method == 'GET', request.method == 'POST']):
        raise MethodNotAllowed()
    if request.method == 'POST':
        try:
            json_data = request.get_json()
        except:
            raise BadRequest()
        if json_data is None:
            raise BadRequest()


UserManagementAPI().mount('/v{:s}/admin'.format(__version__), REST_APPLICATION)
LoginAPI().mount('/v{:s}/login'.format(__version__), REST_APPLICATION)
RegistrationAPI().mount('/v{:s}/registration'.format(__version__), REST_APPLICATION)
