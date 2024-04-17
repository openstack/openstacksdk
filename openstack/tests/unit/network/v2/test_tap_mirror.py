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

from openstack.network.v2 import tap_mirror
from openstack.tests.unit import base


IDENTIFIER = 'IDENTIFIER'
PORT_ID = 'PORT_ID'
EXAMPLE = {
    'name': 'my_tap_mirror',
    'port_id': PORT_ID,
    'directions': {'IN': 99},
    'remote_ip': '193.10.10.1',
    'mirror_type': 'erspanv1',
    'id': IDENTIFIER,
    'project_id': '42',
}


class TestTapMirror(base.TestCase):
    def test_basic(self):
        sot = tap_mirror.TapMirror()
        self.assertEqual('tap_mirror', sot.resource_key)
        self.assertEqual('tap_mirrors', sot.resources_key)
        self.assertEqual('/taas/tap_mirrors', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = tap_mirror.TapMirror(**EXAMPLE)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['port_id'], sot.port_id)
        self.assertEqual(EXAMPLE['directions'], sot.directions)
        self.assertEqual(EXAMPLE['remote_ip'], sot.remote_ip)
        self.assertEqual(EXAMPLE['mirror_type'], sot.mirror_type)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['project_id'], sot.project_id)

        self.assertDictEqual(
            {
                'limit': 'limit',
                'marker': 'marker',
                'name': 'name',
                'project_id': 'project_id',
                'sort_key': 'sort_key',
                'sort_dir': 'sort_dir',
            },
            sot._query_mapping._mapping,
        )
