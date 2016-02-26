#!/bin/env python3.5

"""
Base Launcher Module that initializes the Control Manager
"""

import sys
from .control import manager


if __name__ == '__main__':
    manager.ControlManager.factory(sys.argv)
