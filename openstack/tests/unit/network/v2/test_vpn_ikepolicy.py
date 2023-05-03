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

from openstack.network.v2 import vpn_ike_policy
from openstack.tests.unit import base


EXAMPLE = {
    "auth_algorithm": "1",
    "description": "2",
    "encryption_algorithm": "3",
    "ike_version": "4",
    "lifetime": {'a': 5},
    "name": "5",
    "pfs": "6",
    "project_id": "7",
    "phase1_negotiation_mode": "8",
    "units": "9",
    "value": 10,
}


class TestVpnIkePolicy(base.TestCase):
    def test_basic(self):
        sot = vpn_ike_policy.VpnIkePolicy()
        self.assertEqual('ikepolicy', sot.resource_key)
        self.assertEqual('ikepolicies', sot.resources_key)
        self.assertEqual('/vpn/ikepolicies', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = vpn_ike_policy.VpnIkePolicy(**EXAMPLE)
        self.assertEqual(EXAMPLE['auth_algorithm'], sot.auth_algorithm)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(
            EXAMPLE['encryption_algorithm'], sot.encryption_algorithm
        )
        self.assertEqual(EXAMPLE['ike_version'], sot.ike_version)
        self.assertEqual(EXAMPLE['lifetime'], sot.lifetime)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['pfs'], sot.pfs)
        self.assertEqual(EXAMPLE['project_id'], sot.project_id)
        self.assertEqual(
            EXAMPLE['phase1_negotiation_mode'], sot.phase1_negotiation_mode
        )
        self.assertEqual(EXAMPLE['units'], sot.units)
        self.assertEqual(EXAMPLE['value'], sot.value)
