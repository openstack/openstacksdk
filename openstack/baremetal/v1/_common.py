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


RETRIABLE_STATUS_CODES = [
    # HTTP Conflict - happens if a node is locked
    409,
    # HTTP Service Unavailable happens if there's no free conductor
    503
]
"""HTTP status codes that should be retried."""


PROVISIONING_VERSIONS = {
    'abort': 13,
    'adopt': 17,
    'clean': 15,
    'inspect': 6,
    'manage': 4,
    'provide': 4,
    'rescue': 38,
    'unrescue': 38,
}
"""API microversions introducing provisioning verbs."""


# Based on https://docs.openstack.org/ironic/latest/contributor/states.html
EXPECTED_STATES = {
    'active': 'active',
    'adopt': 'available',
    'clean': 'manageable',
    'deleted': 'available',
    'inspect': 'manageable',
    'manage': 'manageable',
    'provide': 'available',
    'rebuild': 'active',
    'rescue': 'rescue',
}
"""Mapping of provisioning actions to expected stable states."""

STATE_VERSIONS = {
    'enroll': '1.11',
    'manageable': '1.4',
}
"""API versions when certain states were introduced."""

VIF_VERSION = '1.28'
"""API version in which the VIF operations were introduced."""
