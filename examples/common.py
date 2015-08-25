#!/usr/bin/env python
# common.py - Common bits for SDK examples

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
SDK Examples Common

This is a collection of common functions used by the example scripts.

common.object_parser() provides the common set of command-line arguments
used in the library CLIs for setting up authentication.  This should make
playing with the example scripts against a running OpenStack simpler.

Typical environment variables to set and export for authentication include:

    OS_PROJECT_NAME=FooFighter
    OS_PASSWORD=nirvana
    OS_AUTH_URL=https://foofighters.com:35357/v3
    OS_USERNAME=davegrohl
    OS_REGION_NAME=Seattle

"""

import argparse
import logging
import os
import sys
import traceback
import uuid

from openstack import utils

_logger = logging.getLogger('openstack.example')


def find_resource_cls(opts):
    argument = opts.argument
    if argument.find('/') > 0:
        # called with file e.g.: openstack/network/v2/network.py
        args = argument.split('/')
        args[-1] = args[-1].replace('.py', '')
        from_str = '.'.join(args)
        class_str = args[-1].title()
        class_str = class_str.replace('_', '')
    else:
        # called with path e.g.: openstack.network.v2.network.Network
        args = argument.rpartition('.')
        from_str = args[0]
        class_str = args[2]
    __import__(from_str)
    mod = sys.modules[from_str]
    return getattr(mod, class_str)


def get_data_option(opts):
    if not opts.data:
        return opts.data
    try:
        iddy = uuid.UUID(opts.data)
        return {'id': iddy}
    except ValueError:
        data = opts.data
        if data.startswith('openstack.'):
            fullname = data.split('(')[0]
            classname = fullname.split('.')[-1]
            modulename = fullname.replace('.' + classname, '')
            data = data.replace('openstack.',
                                '__import__("' + modulename + '").')
        return eval(data)


def env(*vars, **kwargs):
    """Search for the first defined of possibly many env vars

    Returns the first environment variable defined in vars, or
    returns the default defined in kwargs.

    """
    for v in vars:
        value = os.environ.get(v, None)
        if value:
            return value
    return kwargs.get('default', '')


def option_parser():
    """Set up some of the common CLI options

    These are the basic options that match the library CLIs so
    command-line/environment setups for those also work with these
    demonstration programs.

    """

    parser = argparse.ArgumentParser(
        description='A demonstration framework')
    # Global arguments
    parser.add_argument(
        '--os-cloud',
        dest='cloud',
        metavar='<cloud>',
        default=env('OS_CLOUD', default=None),
        help=('Cloud configuration from ' +
              'https://pypi.python.org/pypi/os-client-config (Env: OS_CLOUD)')
    )
    parser.add_argument(
        '--data',
        metavar='<data>',
        default={},
        help='Json data for command.',
    )
    parser.add_argument(
        '-v', '--verbose',
        action='count',
        dest='verbose_level',
        default=1,
        help='Increase verbosity of output. Can be repeated.',
    )
    parser.add_argument(

        '--debug',
        default=False,
        action='store_true',
        help='show tracebacks on errors',
    )
    parser.add_argument(
        'argument',
        default=None,
        nargs='?',
        help='Argument to use.',
    )
    return parser


def setup():
    opts = option_parser().parse_args()
    utils.enable_logging(opts.debug, stream=sys.stdout)
    return opts


def main(opts, run):
    try:
        return run(opts)
    except Exception as e:
        if opts.debug:
            _logger.error(traceback.format_exc(e))
        else:
            _logger.error('Exception raised: ' + str(e))
        return 1
