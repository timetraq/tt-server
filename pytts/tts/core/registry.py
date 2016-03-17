"""
Implementation Registry of exported functions
"""

from .prog.registration import FUNCTIONS as REGISTRATION
from .prog.administration import FUNCTIONS as ADMINISTRATION


FUNCTIONS = {
    **ADMINISTRATION,
    **REGISTRATION,
}
