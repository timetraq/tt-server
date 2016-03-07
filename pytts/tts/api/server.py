"""
Flask API entry point
"""

from blackred import BlackRed
from flask import Flask, jsonify, request
from werkzeug.exceptions import Unauthorized

from .auth.login import LoginStatusAPI


REST_APPLICATION = Flask(__name__)
BLACKRED = BlackRed()


@REST_APPLICATION.route('/version', methods=('GET',))
def get_version():
    """
    Simply return the version of the API as JSON data

    :return: JSONified version
    """
    return jsonify({'version': '1.0'})


@REST_APPLICATION.before_request
def check_blackred():
    """
    Check if the IP address of the remote user is on the blacklist
    :raises Unauthorized: When the remote user is blocked
    """
    remote_addr = request.remote_addr
    if BLACKRED.is_blocked(remote_addr):
        raise Unauthorized()


LoginStatusAPI().mount('/v1.0/login', REST_APPLICATION)
