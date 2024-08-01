"""
Lightspeed API Wrapper
~~~~~~~~~~~~~~~~~~~

A basic wrapper for the Lightspeed API.

:copyright: (c) 2024-present MCausc78
:license: MIT, see LICENSE for more details.

"""

__title__ = 'lightspeed'
__author__ = 'MCausc78'
__license__ = 'MIT'
__copyright__ = 'Copyright 2024-present MCausc78'
__version__ = '1.0.0a'

__path__ = __import__('pkgutil').extend_path(__path__, __name__)

import logging
from typing import NamedTuple, Literal

from . import (
    abc as abc,
    utils as utils,
)
from .category import *
from .client import *
from .enums import *
from .errors import *
from .invite import *
from .message import *
from .mixins import *
from .object import *
from .region import *
from .stream import *
from .user import *


class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    releaselevel: Literal['alpha', 'beta', 'candidate', 'final']
    serial: int


version_info: VersionInfo = VersionInfo(major=1, minor=0, micro=0, releaselevel='alpha', serial=0)

logging.getLogger(__name__).addHandler(logging.NullHandler())

del logging, NamedTuple, Literal, VersionInfo
