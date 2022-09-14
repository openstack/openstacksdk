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

from openstack.image.v2 import metadef_property
from openstack.tests.unit import base

EXAMPLE = {
    'namespace_name': 'CIM::StorageAllocationSettingData',
    'name': 'Access',
    'type': 'string',
    'title': 'Access',
    'description': (
        'Access describes whether the allocated storage extent is '
        '1 (readable), 2 (writeable), or 3 (both).'
    ),
    'operators': ['<or>'],
    'default': None,
    'readonly': None,
    'minimum': None,
    'maximum': None,
    'enum': [
        'Unknown',
        'Readable',
        'Writeable',
        'Read/Write Supported',
        'DMTF Reserved',
    ],
    'pattern': None,
    'min_length': 0,
    'max_length': None,
    'items': None,
    'unique_items': False,
    'min_items': 0,
    'max_items': None,
    'additional_items': None,
}


class TestMetadefProperty(base.TestCase):
    def test_basic(self):
        sot = metadef_property.MetadefProperty()
        self.assertEqual(
            '/metadefs/namespaces/%(namespace_name)s/properties', sot.base_path
        )
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = metadef_property.MetadefProperty(**EXAMPLE)
        self.assertEqual(EXAMPLE['namespace_name'], sot.namespace_name)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['type'], sot.type)
        self.assertEqual(EXAMPLE['title'], sot.title)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertListEqual(EXAMPLE['operators'], sot.operators)
        self.assertEqual(EXAMPLE['default'], sot.default)
        self.assertEqual(EXAMPLE['readonly'], sot.is_readonly)
        self.assertEqual(EXAMPLE['minimum'], sot.minimum)
        self.assertEqual(EXAMPLE['maximum'], sot.maximum)
        self.assertListEqual(EXAMPLE['enum'], sot.enum)
        self.assertEqual(EXAMPLE['pattern'], sot.pattern)
        self.assertEqual(EXAMPLE['min_length'], sot.min_length)
        self.assertEqual(EXAMPLE['max_length'], sot.max_length)
        self.assertEqual(EXAMPLE['items'], sot.items)
        self.assertEqual(EXAMPLE['unique_items'], sot.require_unique_items)
        self.assertEqual(EXAMPLE['min_items'], sot.min_items)
        self.assertEqual(EXAMPLE['max_items'], sot.max_items)
        self.assertEqual(
            EXAMPLE['additional_items'], sot.allow_additional_items
        )
