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

from openstack.image.v2 import metadef_namespace
from openstack.tests.unit import base

EXAMPLE = {
    'display_name': 'Cinder Volume Type',
    'created_at': '2014-08-28T17:13:06Z',
    'is_protected': True,
    'namespace': 'OS::Cinder::Volumetype',
    'owner': 'admin',
    'resource_type_associations': [
        {
            'created_at': '2014-08-28T17:13:06Z',
            'name': 'OS::Glance::Image',
            'updated_at': '2014-08-28T17:13:06Z'
        }
    ]
}


class TestMetadefNamespace(base.TestCase):
    def test_basic(self):
        sot = metadef_namespace.MetadefNamespace()
        self.assertIsNone(sot.resource_key)
        self.assertEqual('namespaces', sot.resources_key)
        self.assertEqual('/metadefs/namespaces', sot.base_path)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = metadef_namespace.MetadefNamespace(**EXAMPLE)
        self.assertEqual(EXAMPLE['namespace'], sot.namespace)
        self.assertEqual(EXAMPLE['owner'], sot.owner)
        self.assertEqual(EXAMPLE['created_at'], sot.created_at)
        self.assertEqual(EXAMPLE['is_protected'], sot.is_protected)
        self.assertEqual(EXAMPLE['display_name'], sot.display_name)
        self.assertListEqual(EXAMPLE['resource_type_associations'],
                             sot.resource_type_associations)

        self.assertDictEqual(
            {
                'limit': 'limit',
                'marker': 'marker',
                'resource_types': 'resource_types',
                'sort_dir': 'sort_dir',
                'sort_key': 'sort_key',
                'visibility': 'visibility'
            }, sot._query_mapping._mapping)
