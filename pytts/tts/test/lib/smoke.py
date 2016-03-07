"""
Utils for Smoke Tests
"""

from ...util.config import ConfigurationFileFinder


def fetch_configuration() -> dict:
    """
    Fetch configuration from global config file

    :return: Configuration Dictionary
    :rtype: dict
    """
    config = ConfigurationFileFinder().find_as_json()
    assert config is not None
    assert isinstance(config, dict)
    assert 'tts' in config
    tts = config['tts']
    assert isinstance(tts, dict)
    return tts
