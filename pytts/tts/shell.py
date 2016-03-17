# pylint: disable=unused-argument,no-self-use
"""
Create an interactive shell to control the server
"""

from cmd import Cmd
import requests
from redis import StrictRedis

from tts.core.token import token_generator
from tts.util.queue.redis import RedisQueueProducer
from tts.util.config import ConfigurationFileFinder
from tts.util.redis import RedisConfiguration


class PyTTSShell(Cmd):
    """
    Simple shell for working with pytts
    """

    API = 'http://{:s}:{:d}/api/v1.0/admin'.format(
        ConfigurationFileFinder().find_as_json()['tts']['server']['bind_ip'],
        ConfigurationFileFinder().find_as_json()['tts']['server']['bind_port']
    )

    intro = 'PyTTS Interactive Shell'
    prompt = '[PyTTS] $ '

    command_queue_access = RedisQueueProducer(
        configuration=ConfigurationFileFinder().find_as_json()['tts']['queues']['command']
    )

    api_redis = RedisConfiguration(
        configuration=ConfigurationFileFinder().find_as_json()['tts']['queues']['api']
    )

    api_pool = api_redis.create_redis_connection_pool()

    def __webservice_access(self, endpoint: str, data: dict) -> str:
        my_token = token_generator()
        redis = StrictRedis(connection_pool=self.api_pool)
        redis.set('ADMIN_TOKEN:{:s}'.format(my_token), endpoint, ex=5)
        r = requests.post('{:s}/{:s}'.format(self.API, endpoint), json={
            'admin_token': my_token,
            'data': data,
        })
        r.close()
        if not r.ok:
            return 'ERR {:d}: {:s}'.format(r.status_code, r.reason)
        return r.json()

    def do_stop(self, arg):
        """
        Send Stop Command to the Server
        """
        self.command_queue_access.fire_message('STOP')

    def do_enable_user(self, arg):
        """
        Activates a already created user account
        """
        if arg is None or not isinstance(arg, str) or len(arg.strip()) <= 0:
            print('Usage: enable_user <username>')
            return
        print(self.__webservice_access('enable_user', {
           'username': arg.strip(),
        }))

    def do_quit(self, arg):
        """
        Exit interactive Shell
        """
        print('Good Bye!')
        exit(0)


if __name__ == '__main__':
    PyTTSShell().cmdloop()
