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
import json
import logging
import os
import subprocess
import sys
import traceback
import uuid

CONSOLE_MESSAGE_FORMAT = '%(levelname)s: %(name)s %(message)s'
_logger = logging.getLogger(__name__)


def find_resource_cls(opts):
    argument = opts.argument
    if argument.find('/') > 0:
        # called with file e.g.: openstack/network/v2_0/network.py
        args = argument.split('/')
        args[-1] = args[-1].replace('.py', '')
        from_str = '.'.join(args)
        class_str = args[-1].title()
        class_str = class_str.replace('_', '')
    else:
        # called with path e.g.: openstack.network.v2_0.network.Network
        args = argument.rpartition('.')
        from_str = args[0]
        class_str = args[2]
    __import__(from_str)
    mod = sys.modules[from_str]
    return getattr(mod, class_str)


def get_data_option(opts):
    try:
        iddy = uuid.UUID(opts.data)
        return {'id': iddy}
    except ValueError:
        return json.loads(opts.data)


def get_open_fds():
    '''Return the open file descriptors for current process

    .. warning: will only work on UNIX-like os-es.
    '''
    pid = os.getpid()
    procs = subprocess.check_output(
        ["lsof", '-w', '-Fftn0', "-p", str(pid)]
    )
    print('procs: %s' % procs)
    print('netstat: %s' % subprocess.check_output(['netstat', '-nlt']))
    procs_list = filter(
        lambda s: s and s[0] == 'f' and s[1].isdigit(),
        procs.split('\n')
    )
    return [d.replace('\000', '|') for d in procs_list]


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
        '--os-auth-url',
        dest='auth_url',
        metavar='<auth-url>',
        default=env('OS_AUTH_URL'),
        help='Authentication URL (Env: OS_AUTH_URL)',
    )
    parser.add_argument(
        '--os-project-name',
        dest='project_name',
        metavar='<auth-project-name>',
        default=env('OS_PROJECT_NAME', default=env('OS_TENANT_NAME')),
        help='Project name of the requested project-level'
             'authorization scope (Env: OS_PROJECT_NAME)',
    )
    parser.add_argument(
        '--os-domain-name',
        dest='domain_name',
        metavar='<auth-domain-name>',
        default=env('OS_DOMAIN_NAME'),
        help='Domain name for scope of '
             'authorization (Env: OS_DOMAIN_NAME)',
    )
    parser.add_argument(
        '--os-project-domain-name',
        dest='project_domain_name',
        metavar='<auth-project-domain-name>',
        default=env('OS_PROJECT_DOMAIN_NAME'),
        help='Project domain name for scope of '
             'authorization (Env: OS_PROJECT_DOMAIN_NAME)',
    )
    parser.add_argument(
        '--os-user-domain-name',
        dest='user_domain_name',
        metavar='<auth-user-domain-name>',
        default=env('OS_USER_DOMAIN_NAME'),
        help='User domain name for scope of '
             'authorization (Env: OS_USER_DOMAIN_NAME)',
    )
    parser.add_argument(
        '--os-username',
        dest='username',
        metavar='<auth-username>',
        default=env('OS_USERNAME'),
        help='Authentication username (Env: OS_USERNAME)',
    )
    parser.add_argument(
        '--os-password',
        dest='password',
        metavar='<auth-password>',
        default=env('OS_PASSWORD'),
        help='Authentication password (Env: OS_PASSWORD)',
    )
    parser.add_argument(
        '--os-region-name',
        dest='region_name',
        metavar='<region>',
        default=env('OS_REGION_NAME'),
        help='Service region (Env: OS_REGION_NAME)')
    parser.add_argument(
        '--os-cacert',
        dest='cacert',
        metavar='<ca-bundle-file>',
        default=env('OS_CACERT'),
        help='CA certificate bundle file (Env: OS_CACERT)',
    )
    verify_group = parser.add_mutually_exclusive_group()
    verify_group.add_argument(
        '--verify',
        action='store_true',
        help='Verify server certificate (default)',
    )
    verify_group.add_argument(
        '--insecure',
        action='store_true',
        help='Disable server certificate verification',
    )
    parser.add_argument(
        '--os-identity-api-version',
        dest='identity_api_version',
        metavar='<identity-api-version>',
        default=env(
            'OS_IDENTITY_API_VERSION',
            default=None),
        help='Force Identity API version (Env: OS_IDENTITY_API_VERSION)',
    )
    parser.add_argument(
        '--os-token',
        dest='token',
        metavar='<token>',
        default=env('OS_TOKEN'),
        help='Defaults to env[OS_TOKEN]',
    )
    parser.add_argument(
        '--data',
        metavar='<data>',
        default='{}',
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


def configure_logging(opts):
    """Typical app logging setup

    Based on OSC/cliff

    """

    root_logger = logging.getLogger('')

    # Always send higher-level messages to the console via stderr
    console = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter(CONSOLE_MESSAGE_FORMAT)
    console.setFormatter(formatter)
    root_logger.addHandler(console)

    if opts.debug:
        root_logger.setLevel(logging.DEBUG)
    else:
        root_logger.setLevel(logging.WARNING)
    return


def setup():
    opts = option_parser().parse_args()
    configure_logging(opts)
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
