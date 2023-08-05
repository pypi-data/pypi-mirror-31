# -*- coding: utf-8 -*-
# This python package is handling all MOCK communication for rostful-node.
# The point of it is to be able to fully tests the multiprocess behavior,
#     in pure python, without having to run a ROS system.
#
# If possible these should also be base classes for all the possible multiprocess framework interfaces
# available in pyros
#
# Mock interface is provided with the package, because it may help client libraries to implement their own tests
#
from __future__ import absolute_import, division, print_function

import logging

"""
Hopefully this should endup in doc
"""

# create logger
# TODO solve multiprocess logger problem(s)...
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

import pyros_interfaces_common

from .mockinterface import MockInterface
from .mockmessage import (
    extract_values,
    populate_instance,
    FieldTypeMismatchException,
    NonexistentFieldException,
    StatusMsg,
)
from .mockparam import MockParam
from .mockservice import MockService, statusecho_service
from .mocksubscriber import MockSubscriber
from .mockpublisher import MockPublisher
from .mocksystem import MockSystem, statusecho_topic
from .pyros_mock import PyrosMock


# Since this mock interface follows ROS design (params, service, topics)
# We decided to make it part of ROS interface

# TODO : We should probably use mock library for this and test against it...

__all__ = [
    'MockPublisher',
    'MockSubscriber',
    'MockService',
    'MockParam',
    'MockSystem',
    'extract_values',
    'populate_instance',
    'FieldTypeMismatchException',
    'NonexistentFieldException',
    'StatusMsg',
    'statusecho_topic',
    'statusecho_service',
    'MockInterface',
    'PyrosMock',
]
