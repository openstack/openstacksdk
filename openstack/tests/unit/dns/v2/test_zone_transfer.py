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

from openstack.dns.v2 import zone_transfer
from openstack.tests.unit import base


IDENTIFIER = '074e805e-fe87-4cbb-b10b-21a06e215d41'
EXAMPLE_REQUEST = {
    'created_at': '2014-07-17T20:34:40.882579',
    'description': 'some description',
    'id': IDENTIFIER,
    'key': '9Z2R50Y0',
    'project_id': '1',
    'status': 'ACTIVE',
    'target_project_id': '123456',
    'updated_at': None,
    'zone_id': '6b78734a-aef1-45cd-9708-8eb3c2d26ff8',
    'zone_name': 'qa.dev.example.com.',
}
EXAMPLE_ACCEPT = {
    'status': 'COMPLETE',
    'zone_id': 'b4542f5a-f1ea-4ec1-b850-52db9dc3f465',
    'created_at': '2016-06-22 06:13:55',
    'updated_at': 'null',
    'key': 'FUGXMZ5N',
    'project_id': '2e43de7ce3504a8fb90a45382532c37e',
    'id': IDENTIFIER,
    'zone_transfer_request_id': '794fdf58-6e1d-41da-8b2d-16b6d10c8827',
}


class TestZoneTransferRequest(base.TestCase):
    def test_basic(self):
        sot = zone_transfer.ZoneTransferRequest()
        # self.assertEqual('', sot.resource_key)
        self.assertEqual('transfer_requests', sot.resources_key)
        self.assertEqual('/zones/tasks/transfer_requests', sot.base_path)
        self.assertTrue(sot.allow_list)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)

        self.assertDictEqual(
            {'limit': 'limit', 'marker': 'marker', 'status': 'status'},
            sot._query_mapping._mapping,
        )

    def test_make_it(self):
        sot = zone_transfer.ZoneTransferRequest(**EXAMPLE_REQUEST)
        self.assertEqual(IDENTIFIER, sot.id)
        self.assertEqual(EXAMPLE_REQUEST['created_at'], sot.created_at)
        self.assertEqual(EXAMPLE_REQUEST['updated_at'], sot.updated_at)
        self.assertEqual(EXAMPLE_REQUEST['description'], sot.description)
        self.assertEqual(EXAMPLE_REQUEST['key'], sot.key)
        self.assertEqual(EXAMPLE_REQUEST['project_id'], sot.project_id)
        self.assertEqual(EXAMPLE_REQUEST['status'], sot.status)
        self.assertEqual(
            EXAMPLE_REQUEST['target_project_id'], sot.target_project_id
        )
        self.assertEqual(EXAMPLE_REQUEST['zone_id'], sot.zone_id)
        self.assertEqual(EXAMPLE_REQUEST['zone_name'], sot.zone_name)


class TestZoneTransferAccept(base.TestCase):
    def test_basic(self):
        sot = zone_transfer.ZoneTransferAccept()
        # self.assertEqual('', sot.resource_key)
        self.assertEqual('transfer_accepts', sot.resources_key)
        self.assertEqual('/zones/tasks/transfer_accepts', sot.base_path)
        self.assertTrue(sot.allow_list)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertFalse(sot.allow_delete)

        self.assertDictEqual(
            {'limit': 'limit', 'marker': 'marker', 'status': 'status'},
            sot._query_mapping._mapping,
        )

    def test_make_it(self):
        sot = zone_transfer.ZoneTransferAccept(**EXAMPLE_ACCEPT)
        self.assertEqual(IDENTIFIER, sot.id)
        self.assertEqual(EXAMPLE_ACCEPT['created_at'], sot.created_at)
        self.assertEqual(EXAMPLE_ACCEPT['updated_at'], sot.updated_at)
        self.assertEqual(EXAMPLE_ACCEPT['key'], sot.key)
        self.assertEqual(EXAMPLE_ACCEPT['project_id'], sot.project_id)
        self.assertEqual(EXAMPLE_ACCEPT['status'], sot.status)
        self.assertEqual(EXAMPLE_ACCEPT['zone_id'], sot.zone_id)
        self.assertEqual(
            EXAMPLE_ACCEPT['zone_transfer_request_id'],
            sot.zone_transfer_request_id,
        )
