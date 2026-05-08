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

from openstack.network.v2 import security_groups_default_statefulness as sgds
from openstack.tests.unit import base


IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'id': IDENTIFIER,
    'project_id': 'fb0e16da8ce7435c8a44464773e21660',
    'stateful': False,
}


class TestSecurityGroupsDefaultStatefulness(base.TestCase):
    def test_basic(self):
        sot = sgds.SecurityGroupsDefaultStatefulness()
        self.assertEqual(
            'security_groups_default_statefulness', sot.resource_key
        )
        self.assertEqual(
            'security_groups_default_statefulness', sot.resources_key
        )
        self.assertEqual(
            '/security-groups-default-statefulness', sot.base_path
        )
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

        self.assertDictEqual(
            {
                'id': 'id',
                'limit': 'limit',
                'marker': 'marker',
                'project_id': 'project_id',
                'sort_dir': 'sort_dir',
                'sort_key': 'sort_key',
                'stateful': 'stateful',
            },
            sot._query_mapping._mapping,
        )

    def test_make_it(self):
        sot = sgds.SecurityGroupsDefaultStatefulness(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['project_id'], sot.project_id)
        self.assertEqual(EXAMPLE['stateful'], sot.stateful)
