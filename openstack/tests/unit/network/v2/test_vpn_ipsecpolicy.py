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

from openstack.network.v2 import vpn_ipsec_policy
from openstack.tests.unit import base


EXAMPLE = {
    "auth_algorithm": "1",
    "description": "2",
    "encryption_algorithm": "3",
    "lifetime": {'a': 5},
    "name": "5",
    "pfs": "6",
    "project_id": "7",
    "units": "9",
    "value": 10
}


class TestVpnIpsecPolicy(base.TestCase):

    def test_basic(self):
        sot = vpn_ipsec_policy.VpnIpsecPolicy()
        self.assertEqual('ipsecpolicy', sot.resource_key)
        self.assertEqual('ipsecpolicies', sot.resources_key)
        self.assertEqual('/vpn/ipsecpolicies', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = vpn_ipsec_policy.VpnIpsecPolicy(**EXAMPLE)
        self.assertEqual(EXAMPLE['auth_algorithm'], sot.auth_algorithm)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['encryption_algorithm'],
                         sot.encryption_algorithm)
        self.assertEqual(EXAMPLE['lifetime'], sot.lifetime)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['pfs'], sot.pfs)
        self.assertEqual(EXAMPLE['project_id'], sot.project_id)
        self.assertEqual(EXAMPLE['units'], sot.units)
        self.assertEqual(EXAMPLE['value'], sot.value)

        self.assertDictEqual(
            {
                "limit": "limit",
                "marker": "marker",
            },
            sot._query_mapping._mapping)
