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

from openstack.tests.unit import base

from openstack.dns.v2 import recordset


IDENTIFIER = 'NAME'
EXAMPLE = {
    'description': 'This is an example record set.',
    'updated_at': None,
    'records': [
        '10.1.0.2'
    ],
    'ttl': 3600,
    'id': IDENTIFIER,
    'name': 'example.org.',
    'project_id': '4335d1f0-f793-11e2-b778-0800200c9a66',
    'zone_id': '2150b1bf-dee2-4221-9d85-11f7886fb15f',
    'zone_name': 'example.com.',
    'created_at': '2014-10-24T19:59:44.000000',
    'version': 1,
    'type': 'A',
    'status': 'ACTIVE',
    'action': 'NONE'
}


class TestRecordset(base.TestCase):

    def test_basic(self):
        sot = recordset.Recordset()
        self.assertIsNone(sot.resource_key)
        self.assertEqual('recordsets', sot.resources_key)
        self.assertEqual('/zones/%(zone_id)s/recordsets', sot.base_path)
        self.assertTrue(sot.allow_list)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)

        self.assertDictEqual({'data': 'data',
                              'description': 'description',
                              'limit': 'limit',
                              'marker': 'marker',
                              'name': 'name',
                              'status': 'status',
                              'ttl': 'ttl',
                              'type': 'type'},
                             sot._query_mapping._mapping)

    def test_make_it(self):
        sot = recordset.Recordset(**EXAMPLE)
        self.assertEqual(IDENTIFIER, sot.id)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['ttl'], sot.ttl)
        self.assertEqual(EXAMPLE['type'], sot.type)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['status'], sot.status)
