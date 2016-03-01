"""
Flask API entry point
"""

from flask import Flask, jsonify

from .auth.login import LoginStatusAPI


REST_APPLICATION = Flask(__name__)


@REST_APPLICATION.route('/version', methods=['GET'])
def get_version():
    """
    Simply return the version of the API as JSON data

    :return: JSONified version
    """
    return jsonify({'version': '1.0'})


LoginStatusAPI().mount('/v1.0/login', REST_APPLICATION)
