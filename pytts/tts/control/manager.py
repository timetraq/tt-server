"""
This holds stuff to manage our server instance
"""

from os import path

import cherrypy

from ..app.server import StaticServer
from ..util.config import ConfigurationFileFinder
from ..util.queue.redis import RedisQueueConsumer, RedisQueueAccess
from ..util.singleton import SingletonMeta


class ControlManager(object, metaclass=SingletonMeta):
    """
    The Control Manager manages the server instance, like startup and shutdown
    """

    __initialized = False
    command_handler = None
    server = None
    engine = None

    def __init__(self, no_init: bool=False) -> None:
        """
        Initialize with default settings
        :param bool no_init: Do not perform an initialization, because configuration is already on the way
        """
        if no_init:
            return
        self.__initialized = True

    def configure(self, argv: list=None) -> None:
        """
        Configure with command line arguments
        :param list[str] argv: Command line arguments
        :raises RuntimeError: when already initialized
        """
        if self.initialized:
            raise RuntimeError('ControlManager already initialized')
        self.__initialized = True
        if argv is None:
            return

    @property
    def initialized(self) -> bool:
        """
        Is the class already initialized?
        :return: true, when the class is already initialized
        :rtype: bool
        """
        return self.__initialized

    def stop(self):
        """
        Stop the command handler
        """
        if self.command_handler is not None:
            self.command_handler.stop()
        if self.server is not None:
            self.engine.stop()
            self.server.stop()
            self.server.bus.exit()

    def start(self):
        """
        Start the server

        :raises SystemError: When Server already defined
        """
        if self.server is not None:
            raise SystemError('Server already defined')
        static_path = path.abspath(path.join(
            path.dirname(__file__),
            '..',
            'app',
            'static'
        ))
        csp_sources = ['default', 'script', 'style', 'img', 'connect', 'font', 'object', 'media', 'frame']
        csp_default_source = "'self'"
        csp_rules = list()
        for csp_source in csp_sources:
            csp_rules.append('{:s}-src {:s}'.format(csp_source, csp_default_source))
        csp = '; '.join(csp_rules)
        cherrypy.tree.mount(StaticServer(), '/', config={
            '/static': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': static_path,
                'tools.encode.on': False,
                'tools.response_headers.on': True,
                'tools.response_headers.headers': [
                    ('X-Frame-Options', 'DENY'),
                    ('X-XSS-Protection', '1; mode=block'),
                    ('Content-Security-Policy', csp),
                    ('X-Content-Security-Policy', csp),
                    ('X-Webkit-CSP', csp),
                    ('X-Content-Type-Options', 'nosniff'),
                ],
                'tools.staticdir.content_types': {
                    'html': 'application/xhtml+xml; charset=utf-8',
                    'js': 'application/javascript; charset=utf-8',
                    'css': 'text/css; charset=utf-8',
                    'png': 'image/png',
                },
            },
        })
        self.server = cherrypy.server
        self.server.socket_host = '127.0.0.1'
        self.server.socket_port = 8080
        config = ConfigurationFileFinder().find_as_json()['tts']
        if 'server' in config and 'bind_ip' in config['server']:
            self.server.socket_host = config['server']['bind_ip']
        if 'server' in config and 'bind_port' in config['server']:
            self.server.socket_port = config['server']['bind_port']
        self.server.thread_pool = 30
        self.server.subscribe()
        self.engine = cherrypy.engine
        self.engine.start()

    def manage(self, command: bytes) -> None:
        """
        Manage incoming commands

        :param command: The raw command
        """
        callback_functions = {
            'stop': self.stop,
            'start': self.start,
        }

        cmd = command.decode(encoding='UTF-8').lower()
        if cmd not in callback_functions.keys():
            raise SyntaxError('Invalid Command')
        callback_functions[cmd]()

    @staticmethod
    def factory(argv: list=None) -> 'ControlManager':
        """
        Create a new Control Manager with command line arguments (optional)

        :param list[str] argv: optional command line arguments
        :rtype: ControlManager
        :return: newly created and configured instance
        :raises RuntimeError: when factory was already run
        """
        control_manager = ControlManager(no_init=True)
        if control_manager.initialized:
            raise RuntimeError('ControlManager already initialized')
        control_manager.configure(argv)
        config = ConfigurationFileFinder().find_as_json()['tts']['queues']['command']
        queue_access = RedisQueueAccess(config)
        queue_access.get_connection().delete(queue_access.queue)
        control_manager.command_handler = RedisQueueConsumer(
            config, control_manager.manage
        )
        return control_manager
