"""
Base for Server Tests
"""

from time import sleep

from ...control.manager import ControlManager
from ...util.config import ConfigurationFileFinder
from ...util.singleton import SingletonMeta


def prepare_test(cls_instance):
    """
    Setup the server class
    :param cls_instance: CLS
    """
    cls_instance.ctrl_manager = ControlManager.factory()
    cls_instance.ctrl_manager.start()
    cls_instance.config = {
        'bind_ip': '127.0.0.1',
        'bind_port': 8080,
    }
    config = ConfigurationFileFinder().find_as_json()['tts']
    if 'server' in config and 'bind_ip' in config['server']:
        cls_instance.config['bind_ip'] = config['server']['bind_ip']
    if 'server' in config and 'bind_port' in config['server']:
        cls_instance.config['bind_port'] = config['server']['bind_port']


def cleanup(cls_instance):
    """
    Shutdown stuff
    :param cls_instance: CLS
    """
    cls_instance.ctrl_manager.stop()
    sleep(5)
    SingletonMeta.delete(ConfigurationFileFinder)
    SingletonMeta.delete(ControlManager)
