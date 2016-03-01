"""
Base for Browser Tests (with selenium)
"""

from selenium.webdriver import Firefox
from .server import prepare_test as server_prepare_test, cleanup as server_cleanup


def prepare_test(cls_instance):
    """
    Prepare for Browser Tests

    :param cls_instance: CLS
    """
    server_prepare_test(cls_instance)
    cls_instance.webdriver = Firefox()
    cls_instance.webdriver.implicitly_wait(5)


def cleanup(cls_instance):
    """
    Clean up after tests

    :param cls_instance: CLS
    """
    cls_instance.webdriver.close()
    cls_instance.webdriver.quit()
    server_cleanup(cls_instance)
