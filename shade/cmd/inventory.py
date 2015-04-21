#!/usr/bin/env python
# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import json
import sys
import yaml

import shade
import shade.inventory


def output_format_dict(data, use_yaml):
    if use_yaml:
        return yaml.safe_dump(data, default_flow_style=False)
    else:
        return json.dumps(data, sort_keys=True, indent=2)


def parse_args():
    parser = argparse.ArgumentParser(description='OpenStack Inventory Module')
    parser.add_argument('--refresh', action='store_true',
                        help='Refresh cached information')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--list', action='store_true',
                       help='List active servers')
    group.add_argument('--host', help='List details about the specific host')
    parser.add_argument('--yaml', action='store_true', default=False,
                        help='Output data in nicely readable yaml')
    parser.add_argument('--debug', action='store_true', default=False,
                        help='Enable debug output')
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        shade.simple_logging(debug=args.debug)
        inventory = shade.inventory.OpenStackInventory(
            refresh=args.refresh)
        if args.list:
            output = inventory.list_hosts()
        elif args.host:
            output = inventory.get_host(args.host)
        print(output_format_dict(output, args.yaml))
    except shade.OpenStackCloudException as e:
        sys.stderr.write(e.message + '\n')
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
