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
from unittest import mock

from keystoneauth1 import adapter

from openstack.dns.v2 import zone_import
from openstack.tests.unit import base

IDENTIFIER = '074e805e-fe87-4cbb-b10b-21a06e215d41'
EXAMPLE = {
    'status': 'COMPLETE',
    'zone_id': '6625198b-d67d-47dc-8d29-f90bd60f3ac4',
    'links': {
        'self': 'http://127.0.0.1:9001/v2/zones/tasks/imports/074e805e-f',
        'href': 'http://127.0.0.1:9001/v2/zones/6625198b-d67d-'
    },
    'created_at': '2015-05-08T15:43:42.000000',
    'updated_at': '2015-05-08T15:43:43.000000',
    'version': 2,
    'message': 'example.com. imported',
    'project_id': 'noauth-project',
    'id': IDENTIFIER
}


@mock.patch.object(zone_import.ZoneImport, '_translate_response', mock.Mock())
class TestZoneImport(base.TestCase):

    def test_basic(self):
        sot = zone_import.ZoneImport()
        self.assertEqual('', sot.resource_key)
        self.assertEqual('imports', sot.resources_key)
        self.assertEqual('/zones/tasks/import', sot.base_path)
        self.assertTrue(sot.allow_list)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertTrue(sot.allow_delete)

        self.assertDictEqual({'limit': 'limit',
                              'marker': 'marker',
                              'message': 'message',
                              'status': 'status',
                              'zone_id': 'zone_id'},
                             sot._query_mapping._mapping)

    def test_make_it(self):
        sot = zone_import.ZoneImport(**EXAMPLE)
        self.assertEqual(IDENTIFIER, sot.id)
        self.assertEqual(EXAMPLE['created_at'], sot.created_at)
        self.assertEqual(EXAMPLE['updated_at'], sot.updated_at)
        self.assertEqual(EXAMPLE['version'], sot.version)
        self.assertEqual(EXAMPLE['message'], sot.message)
        self.assertEqual(EXAMPLE['project_id'], sot.project_id)
        self.assertEqual(EXAMPLE['status'], sot.status)
        self.assertEqual(EXAMPLE['zone_id'], sot.zone_id)

    def test_create(self):
        sot = zone_import.ZoneImport()
        response = mock.Mock()
        response.json = mock.Mock(return_value='')
        self.session = mock.Mock(spec=adapter.Adapter)
        self.session.default_microversion = '1.1'

        sot.create(self.session)
        self.session.post.assert_called_once_with(
            mock.ANY, json=None,
            headers={'content-type': 'text/dns'},
            microversion=self.session.default_microversion)
