# pylint: disable=unused-argument,no-self-use
"""
Create an interactive shell to control the server
"""

from cmd import Cmd

from tts.util.queue.redis import RedisQueueProducer
from tts.util.config import ConfigurationFileFinder


class PyTTSShell(Cmd):
    """
    Simple shell for working with pytts
    """

    intro = 'PyTTS Interactive Shell'
    prompt = '[PyTTS] $ '

    command_queue_access = RedisQueueProducer(
        configuration=ConfigurationFileFinder().find_as_json()['tts']['queues']['command']
    )

    def do_stop(self, arg):
        """
        Send Stop Command to the Server
        """
        self.command_queue_access.fire_message('STOP')

    def do_quit(self, arg):
        """
        Exit interactive Shell
        """
        print('Good Bye!')
        exit(0)


if __name__ == '__main__':
    PyTTSShell().cmdloop()
