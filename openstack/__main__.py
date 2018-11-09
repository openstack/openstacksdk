# Copyright (c) 2018 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import sys

import pbr.version


def show_version(args):
    print("OpenstackSDK Version %s" %
          pbr.version.VersionInfo('openstacksdk').version_string_with_vcs())


parser = argparse.ArgumentParser(description="Openstack SDK")
subparsers = parser.add_subparsers(title='commands',
                                   dest='command')

cmd_version = subparsers.add_parser('version',
                                    help='show Openstack SDK version')
cmd_version.set_defaults(func=show_version)

args = parser.parse_args()

if not args.command:
    parser.print_help()
    sys.exit(1)

args.func(args)
