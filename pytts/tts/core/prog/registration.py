"""
Registration Handling
"""

from json import dumps, loads
from uuid import uuid4

from redis import StrictRedis

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

    def choose_username(self, data: dict) -> dict:
        """
        Preparation Step

        :param data: Incoming Data
        :return: Response Data
        :rtype: dict
        """
        key = 'REG_{:s}'.format(data['registration_key'])
        redis = StrictRedis(connection_pool=self.__connection_pool)
        state = redis.get(key)
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
        internal_data['username'] = data['username']
        new_key = str(uuid4())
        new_token = token_generator()
        save_back = {
            'ip': data['ip'],
            'key': new_key,
            'data': internal_data,
            'token': new_token,
            'step': 2,
        }
        redis.set('REG_{:s}'.format(new_key), dumps(save_back), ex=self.__expiration_time)
        return {
            'registration_key': new_key,
            'token': new_token,
            'username': data['username'],
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
        }


FUNCTIONS = Registration().export()
