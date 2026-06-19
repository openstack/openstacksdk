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

from openstack.block_storage.v3 import manageable_volume
from openstack.tests.unit import base

EXAMPLE = {
    'reference': {'source-name': 'volume-00000001'},
    'size': 1,
    'safe_to_manage': True,
    'reason_not_safe': None,
    'cinder_id': None,
    'extra_info': None,
}


class TestManageableVolume(base.TestCase):
    def test_basic(self):
        sot = manageable_volume.ManageableVolume()
        self.assertEqual('manageable-volume', sot.resource_key)
        self.assertEqual('manageable-volumes', sot.resources_key)
        self.assertEqual('/manageable_volumes', sot.base_path)
        self.assertTrue(sot.allow_list)
        self.assertFalse(sot.allow_fetch)
        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.allow_commit)
        self.assertFalse(sot.allow_delete)

        self.assertDictEqual(
            {
                'cluster': 'cluster',
                'host': 'host',
                'limit': 'limit',
                'marker': 'marker',
                'offset': 'offset',
                'sort': 'sort',
            },
            sot._query_mapping._mapping,
        )

    def test_make_it(self):
        sot = manageable_volume.ManageableVolume(**EXAMPLE)
        self.assertEqual(EXAMPLE['reference'], sot.reference)
        self.assertEqual(EXAMPLE['size'], sot.size)
        self.assertTrue(sot.safe_to_manage)
        self.assertIsNone(sot.reason_not_safe)
        self.assertIsNone(sot.cinder_id)
        self.assertIsNone(sot.extra_info)
