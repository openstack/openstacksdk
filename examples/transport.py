#!/usr/bin/env python
# transport.py - Example transport usage

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
SDK Transport Examples

This script shows the basic use of the Transport class in making
REST API calls.

"""

import sys

from examples import common


def do_transport(opts):
    trans = common.run_transport(opts)

    # Get the version data from the auth URL
    resp = trans.get(opts.os_auth_url).json()
    ver = resp['version']
    print("\nAuth URL: %s" % opts.os_auth_url)
    print("  version: %s" % ver['id'])
    print("  status: %s" % ver['status'])

    # Do a basic call to somewhere fun
    url = 'https://api.github.com/users/openstack'
    resp = trans.get(url).json()
    print("\nGitHub API URL: %s" % url)
    print("  gists: %s" % resp['gists_url'])
    print("  repos: %s" % resp['public_repos'])

    url = 'https://api.github.com/users/openstack-dev'
    resp = trans.get(url).json()
    print("\nGitHub API URL: %s" % url)
    print("  gists: %s" % resp['gists_url'])
    print("  repos: %s" % resp['public_repos'])

    # stats
    print('\nTransport connection pools:')
    print("  http pool: %s" % (
        trans.adapters['http://'].poolmanager.pools.keys(),
    ))
    print("  https pool: %s" % (
        trans.adapters['https://'].poolmanager.pools.keys(),
    ))


if __name__ == "__main__":
    opts = common.setup()
    sys.exit(common.main(opts, do_transport))
