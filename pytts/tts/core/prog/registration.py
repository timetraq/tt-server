"""
Registration Handling
"""

from json import dumps, loads
import re
from uuid import uuid4

from redis import StrictRedis

from ...core.lib.db import UserDatabaseConnectivity
from ...core.lib.hash import hash_password_with_base64_salt_as_base64_string, create_salt_as_base64_string
from ...core.token import token_generator
from ...util.config import ConfigurationFileFinder
from ...util.redis import RedisConfiguration


class Registration(RedisConfiguration):
    """
    Registration Implementation
    """

    def __init__(self):
        """
        Initialize Registration
        """
        configuration = ConfigurationFileFinder().find_as_json()['tts']['registration']
        super(Registration, self).__init__(configuration)
        self.__user_db = UserDatabaseConnectivity()
        self.__connection_pool = self.create_redis_connection_pool()
        self.__expiration_time = 3600
        if 'lifetime' in configuration:
            self.__expiration_time = configuration['lifetime']

    def prepare(self, data: dict) -> dict:
        """
        Preparation Step

        :param data: Incoming Data
        :return: Response Data
        :rtype: dict
        """
        redis = StrictRedis(connection_pool=self.__connection_pool)
        registration_key = str(uuid4())
        token = token_generator()
        step_data = {
            'step': 1,
            'ip': data['ip'],
            'key': registration_key,
            'data': {},
            'token': token,
        }
        key = 'REG_{:s}'.format(registration_key)
        redis.set(key, dumps(step_data), ex=self.__expiration_time)
        return {
            'registration_key': registration_key,
            'token': token,
        }

    def __get_key(self, key) -> (str, bytes):
        key_x = 'REG_{:s}'.format(key)
        redis = StrictRedis(connection_pool=self.__connection_pool)
        state = redis.get(key_x)
        return key_x, state, redis

    def choose_username(self, data: dict) -> dict:
        """
        Username selection Step

        :param data: Incoming Data
        :return: Response Data
        :rtype: dict
        """
        key, state, redis = self.__get_key(data['registration_key'])
        if state is None:
            return {'error': {'code': -10001, 'message': 'invalid_registration_key'}}
        state = loads(state.decode('utf-8'), encoding='utf-8')
        if any(['step' not in state, state['step'] != 1]):
            return {'error': {'code': -10002, 'message': 'invalid_registration_step'}}
        redis.delete(key)
        if any(['token' not in state, state['token'] != data['token']]):
            return {'error': {'code': -10003, 'message': 'invalid_registration_token'}}
        if any(['ip' not in state, state['ip'] != data['ip']]):
            return {'error': {'code': -10004, 'message': 'access_denied'}}
        internal_data = {}
        if all(['data' in state, isinstance(state['data'], dict)]):
            internal_data = state['data']
        username_to_check = data['username']
        step = 1
        suc = self.__user_db.collection
        user_obj = suc.find_one({
            'username': re.compile('^' + re.escape(username_to_check) + '$', re.IGNORECASE),
        })
        if user_obj is None:
            internal_data['username'] = username_to_check
            step = 2
        new_key = str(uuid4())
        new_token = token_generator()
        save_back = {
            'ip': data['ip'],
            'key': new_key,
            'data': internal_data,
            'token': new_token,
            'step': step,
        }
        redis.set('REG_{:s}'.format(new_key), dumps(save_back), ex=self.__expiration_time)
        if step == 1:
            return {
                'registration_key': new_key,
                'token': new_token,
                'username_message': 'username_not_available',
            }
        else:
            return {
                'registration_key': new_key,
                'token': new_token,
                'username_message': 'username_available',
                'username': username_to_check,
            }

    def set_password(self, data: dict) -> dict:
        """
        Set the password for the new user

        :param data: Data from the outside
        :return: result data
        :rtype: dict
        """
        key, state, redis = self.__get_key(data['registration_key'])
        if state is None:
            return {'error': {'code': -10001, 'message': 'invalid_registration_key'}}
        state = loads(state.decode('utf-8'), encoding='utf-8')
        if any(['step' not in state, state['step'] != 2]):
            return {'error': {'code': -10002, 'message': 'invalid_registration_step'}}
        redis.delete(key)
        if any(['token' not in state, state['token'] != data['token']]):
            return {'error': {'code': -10003, 'message': 'invalid_registration_token'}}
        if any(['ip' not in state, state['ip'] != data['ip']]):
            return {'error': {'code': -10004, 'message': 'access_denied'}}
        salt = create_salt_as_base64_string()
        pw_hash = hash_password_with_base64_salt_as_base64_string(data['password'], salt)
        user_document = {
            'username': state['data']['username'],
            'salt': salt,
            'password': pw_hash,
            'enabled': False,
        }
        suc = self.__user_db.collection
        user_obj = suc.find_one({
            'username': re.compile('^' + re.escape(state['data']['username']) + '$', re.IGNORECASE),
        })
        if user_obj is not None:
            return {'error': {'code': -10005, 'message': 'registration_failed_username_already_taken'}}
        suc.insert(user_document)
        return {
            'message': 'registration_successful',
            'account_enabled': False,
            'username': state['data']['username'],
        }

    def export(self) -> dict:
        """
        Export functions

        :return: Function dictionary
        :rtype: dict
        """
        return {
            'registration:prepare': self.prepare,
            'registration:choose_username': self.choose_username,
            'registration:set_password': self.set_password,
        }


FUNCTIONS = Registration().export()
