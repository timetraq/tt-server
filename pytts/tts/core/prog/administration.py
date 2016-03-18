"""
Administrative stuff
"""

from ...core.lib.db import UserDatabaseConnectivity
from ...core.lib.hash import create_salt_as_base64_string, hash_password_with_base64_salt_as_base64_string
from ..rules import RULE_USERNAME, RULE_PASSWORD


class UserAdministration(object):

    def __init__(self):
        self.__user_db = UserDatabaseConnectivity()

    def enable_user(self, data: dict) -> dict:
        """
        Enable a user

        :param dict data: Data from call
        :return: Result dict
        :rtype: dict
        """
        if data is None or 'username' not in data or not isinstance(data['username'], str):
            return {'error': {'code': -10001, 'message': 'invalid_data'}}
        username = data['username']
        if not RULE_USERNAME.match(username):
            return {'error': {'code': -10002, 'message': 'invalid_username'}}
        user = self.__user_db.collection.find_one({'username': username})
        if user is None:
            return {'error': {'code': -10003, 'message': 'user_not_found'}}
        if user['enabled']:
            return {'error': {'code': -10004, 'message': 'user_already_enabled'}}
        user['enabled'] = True
        self.__user_db.collection.save(user)
        return {'success': {'message': 'User enabled'}}

    def disable_user(self, data: dict) -> dict:
        """
        Disable a user

        :param dict data: Data from call
        :return: Result dict
        :rtype: dict
        """
        if data is None or 'username' not in data or not isinstance(data['username'], str):
            return {'error': {'code': -10001, 'message': 'invalid_data'}}
        username = data['username']
        if not RULE_USERNAME.match(username):
            return {'error': {'code': -10002, 'message': 'invalid_username'}}
        user = self.__user_db.collection.find_one({'username': username})
        if user is None:
            return {'error': {'code': -10003, 'message': 'user_not_found'}}
        if not user['enabled']:
            return {'error': {'code': -10004, 'message': 'user_already_disabled'}}
        user['enabled'] = False
        self.__user_db.collection.save(user)
        return {'success': {'message': 'User disabled'}}

    def set_password(self, data: dict) -> dict:
        """
        Set the password for a user

        :param dict data: The data from the call
        :return: Response dictionary
        :rtype: dict
        """
        if data is None or 'username' not in data or not isinstance(data['username'], str) \
                or 'password' not in data or not isinstance(data['password'], str):
            return {'error': {'code': -10001, 'message': 'invalid_data'}}
        username = data['username']
        if not RULE_USERNAME.match(username):
            return {'error': {'code': -10002, 'message': 'invalid_username'}}
        password = data['password']
        if not RULE_PASSWORD.match(password):
            return {'error': {'code': -10003, 'message': 'invalid_password'}}
        user = self.__user_db.collection.find_one({'username': username})
        if user is None:
            return {'error': {'code': -10004, 'message': 'user_not_found'}}
        new_salt = create_salt_as_base64_string()
        user['salt'] = new_salt
        user['password'] = hash_password_with_base64_salt_as_base64_string(password, new_salt)
        self.__user_db.collection.save(user)
        return {'success': {'message': 'User password changed'}}

    def export(self):
        """
        Export functions

        :return: Function dictionary
        :rtype: dict
        """
        return {
            'admin:enable_user': self.enable_user,
            'admin:disable_user': self.disable_user,
            'admin:set_password': self.set_password,
        }


FUNCTIONS = UserAdministration().export()
