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
util
--------------------------------

Util methods for functional tests
"""
import operator
import os


def pick_flavor(flavors):
    """Given a flavor list pick the smallest one."""
    # Enable running functional tests against rax - which requires
    # performance flavors be used for boot from volume
    flavor_name = os.environ.get('OPENSTACKSDK_FLAVOR')
    if flavor_name:
        for flavor in flavors:
            if flavor.name == flavor_name:
                return flavor
        return None

    for flavor in sorted(
            flavors,
            key=operator.attrgetter('ram')):
        if 'performance' in flavor.name:
            return flavor
    for flavor in sorted(
            flavors,
            key=operator.attrgetter('ram')):
        return flavor
