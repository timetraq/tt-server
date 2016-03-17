"""
Administrative stuff
"""

from ...core.lib.db import UserDatabaseConnectivity
from ..rules import RULE_USERNAME


class UserAdministration(object):

    def __init__(self):
        self.__user_db = UserDatabaseConnectivity()

    def enable_user(self, data: dict) -> dict:
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

    def export(self):
        """
        Export functions

        :return: Function dictionary
        :rtype: dict
        """
        return {
            'admin:enable_user': self.enable_user,
        }


FUNCTIONS = UserAdministration().export()