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

from openstack.image.v2 import metadef_schema
from openstack.tests.unit import base


IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'name': 'namespace',
    'properties': {
        'namespace': {
            'type': 'string',
            'description': 'The unique namespace text.',
            'maxLength': 80,
        },
        'visibility': {
            'type': 'string',
            'description': 'Scope of namespace accessibility.',
            'enum': ['public', 'private'],
        },
        'created_at': {
            'type': 'string',
            'readOnly': True,
            'description': 'Date and time of namespace creation',
            'format': 'date-time',
        },
        'resource_type_associations': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'prefix': {'type': 'string'},
                    'properties_target': {'type': 'string'},
                },
            },
        },
        'properties': {'$ref': '#/definitions/property'},
        'objects': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'description': {'type': 'string'},
                    'required': {'$ref': '#/definitions/stringArray'},
                    'properties': {'$ref': '#/definitions/property'},
                },
            },
        },
        'tags': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {'name': {'type': 'string'}},
            },
        },
    },
    'additionalProperties': False,
    'definitions': {
        'positiveInteger': {'type': 'integer', 'minimum': 0},
        'positiveIntegerDefault0': {
            'allOf': [
                {'$ref': '#/definitions/positiveInteger'},
                {'default': 0},
            ]
        },
        'stringArray': {
            'type': 'array',
            'items': {'type': 'string'},
            'uniqueItems': True,
        },
    },
    'required': ['namespace'],
}


class TestMetadefSchema(base.TestCase):
    def test_basic(self):
        sot = metadef_schema.MetadefSchema()
        self.assertIsNone(sot.resource_key)
        self.assertIsNone(sot.resources_key)
        self.assertEqual('/schemas/metadefs', sot.base_path)
        self.assertFalse(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertFalse(sot.allow_delete)
        self.assertFalse(sot.allow_list)

    def test_make_it(self):
        sot = metadef_schema.MetadefSchema(**EXAMPLE)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['properties'], sot.properties)
        self.assertEqual(
            EXAMPLE['additionalProperties'], sot.additional_properties
        )
        self.assertEqual(EXAMPLE['definitions'], sot.definitions)
        self.assertEqual(EXAMPLE['required'], sot.required)
