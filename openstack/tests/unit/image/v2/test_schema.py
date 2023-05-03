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

from openstack.image.v2 import schema
from openstack.tests.unit import base


IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'additionalProperties': {'type': 'string'},
    'links': [
        {'href': '{self}', 'rel': 'self'},
        {'href': '{file}', 'rel': 'enclosure'},
        {'href': '{schema}', 'rel': 'describedby'},
    ],
    'name': 'image',
    'properties': {
        'architecture': {
            'description': 'Operating system architecture',
            'is_base': False,
            'type': 'string',
        },
        'visibility': {
            'description': 'Scope of image accessibility',
            'enum': ['public', 'private'],
            'type': 'string',
        },
    },
}


class TestSchema(base.TestCase):
    def test_basic(self):
        sot = schema.Schema()
        self.assertIsNone(sot.resource_key)
        self.assertIsNone(sot.resources_key)
        self.assertEqual('/schemas', sot.base_path)
        self.assertFalse(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertFalse(sot.allow_delete)
        self.assertFalse(sot.allow_list)

    def test_make_it(self):
        sot = schema.Schema(**EXAMPLE)
        self.assertEqual(EXAMPLE['properties'], sot.properties)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(
            EXAMPLE['additionalProperties'], sot.additional_properties
        )
