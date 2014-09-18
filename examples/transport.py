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
Transport Example

For example:
    python -m examples.transport \
           https://region-a.geo-1.identity.hpcloudsvc.com:35357/
"""

import sys

from examples import common
from openstack import transport


def make_transport(opts):
    return transport.Transport(verify=opts.verify)


def run_transport(opts):
    """Create a transport given some options."""
    argument = opts.argument
    trans = make_transport(opts)
    print("transport: %s" % trans)
    print(trans.get(argument).text)
    return


if __name__ == "__main__":
    opts = common.setup()
    sys.exit(common.main(opts, run_transport))
