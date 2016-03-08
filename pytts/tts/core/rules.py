"""
Rules for several entities
"""

import re


RULE_TOKEN = re.compile(r'^[A-Za-z0-9]{64}$', re.DOTALL)
RULE_USERNAME = re.compile(r'^[A-Za-z0-9]{3,32}$', re.DOTALL)
RULE_PASSWORD = re.compile(r'^.{8,255}$', re.DOTALL)
RULE_UUID = re.compile(r'^[A-Fa-f0-9]{8}\-[A-Fa-f0-9]{4}\-[A-Fa-f0-9]{4}\-[A-Fa-f0-9]{4}\-[A-Fa-f0-9]{12}$', re.DOTALL)
