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

from openstack.image.v2 import metadef_object
from openstack.tests.unit import base


EXAMPLE = {
    'created_at': '2014-09-19T18:20:56Z',
    'description': 'The CPU limits with control parameters.',
    'name': 'CPU Limits',
    'properties': {
        'quota:cpu_period': {
            'description': 'The enforcement interval',
            'maximum': 1000000,
            'minimum': 1000,
            'title': 'Quota: CPU Period',
            'type': 'integer',
        },
        'quota:cpu_quota': {
            'description': 'The maximum allowed bandwidth',
            'title': 'Quota: CPU Quota',
            'type': 'integer',
        },
        'quota:cpu_shares': {
            'description': 'The proportional weighted',
            'title': 'Quota: CPU Shares',
            'type': 'integer',
        },
    },
    'required': [],
    'schema': '/v2/schemas/metadefs/object',
    'updated_at': '2014-09-19T18:20:56Z',
}


class TestMetadefObject(base.TestCase):
    def test_basic(self):
        sot = metadef_object.MetadefObject()
        self.assertIsNone(sot.resource_key)
        self.assertEqual('objects', sot.resources_key)
        test_base_path = '/metadefs/namespaces/%(namespace_name)s/objects'
        self.assertEqual(test_base_path, sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = metadef_object.MetadefObject(**EXAMPLE)
        self.assertEqual(EXAMPLE['created_at'], sot.created_at)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['properties'], sot.properties)
        self.assertEqual(EXAMPLE['required'], sot.required)
        self.assertEqual(EXAMPLE['updated_at'], sot.updated_at)
        self.assertDictEqual(
            {
                "limit": "limit",
                "marker": "marker",
                "visibility": "visibility",
                "resource_types": "resource_types",
                "sort_key": "sort_key",
                "sort_dir": "sort_dir",
            },
            sot._query_mapping._mapping,
        )
