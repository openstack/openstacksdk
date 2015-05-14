# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
test_cloud_endpoints
----------------------------------

Tests Keystone endpoints commands.
"""

from mock import patch
import os_client_config
from shade import OperatorCloud
from shade.tests.fakes import FakeEndpoint
from shade.tests.unit import base


# ToDo: support v3 api (dguerri)
class TestCloudEndpoints(base.TestCase):
    mock_endpoints = [
        {'id': 'id1', 'service_id': 'sid1', 'region': 'region1',
         'publicurl': 'purl1', 'internalurl': None, 'adminurl': None},
        {'id': 'id2', 'service_id': 'sid2', 'region': 'region1',
         'publicurl': 'purl2', 'internalurl': None, 'adminurl': None},
        {'id': 'id3', 'service_id': 'sid3', 'region': 'region2',
         'publicurl': 'purl3', 'internalurl': 'iurl3', 'adminurl': 'aurl3'}
    ]

    def setUp(self):
        super(TestCloudEndpoints, self).setUp()
        config = os_client_config.OpenStackConfig()
        self.client = OperatorCloud(
            cloud_config=config.get_one_cloud(validate=False))
        self.mock_ks_endpoints = \
            [FakeEndpoint(**kwa) for kwa in self.mock_endpoints]

    @patch.object(OperatorCloud, 'list_services')
    @patch.object(OperatorCloud, 'keystone_client')
    def test_create_endpoint(self, mock_keystone_client, mock_list_services):
        mock_list_services.return_value = [
            {
                'id': 'service_id1',
                'name': 'service1',
                'type': 'type1',
                'description': 'desc1'
            }
        ]
        mock_keystone_client.endpoints.create.return_value = \
            self.mock_ks_endpoints[0]

        endpoint = self.client.create_endpoint(
            service_name_or_id='service1',
            region='mock_region',
            public_url='mock_public_url',
            internal_url='mock_internal_url',
            admin_url='mock_admin_url'
        )

        mock_keystone_client.endpoints.create.assert_called_with(
            service_id='service_id1',
            region='mock_region',
            publicurl='mock_public_url',
            internalurl='mock_internal_url',
            adminurl='mock_admin_url'
        )

        # test keys and values are correct
        for k, v in self.mock_endpoints[0].items():
            self.assertEquals(v, endpoint.get(k))

    @patch.object(OperatorCloud, 'keystone_client')
    def test_list_endpoints(self, mock_keystone_client):
        mock_keystone_client.endpoints.list.return_value = \
            self.mock_ks_endpoints

        endpoints = self.client.list_endpoints()
        mock_keystone_client.endpoints.list.assert_called_with()

        # test we are getting exactly len(self.mock_endpoints) elements
        self.assertEqual(len(self.mock_endpoints), len(endpoints))

        # test keys and values are correct
        for mock_endpoint in self.mock_endpoints:
            found = False
            for e in endpoints:
                if e['id'] == mock_endpoint['id']:
                    found = True
                    for k, v in mock_endpoint.items():
                        self.assertEquals(v, e.get(k))
                        break
            self.assertTrue(
                found, msg="endpoint {id} not found!".format(
                    id=mock_endpoint['id']))

    @patch.object(OperatorCloud, 'keystone_client')
    def test_search_endpoints(self, mock_keystone_client):
        mock_keystone_client.endpoints.list.return_value = \
            self.mock_ks_endpoints

        # Search by id
        endpoints = self.client.search_endpoints(id='id3')
        # # test we are getting exactly 1 element
        self.assertEqual(1, len(endpoints))
        for k, v in self.mock_endpoints[2].items():
            self.assertEquals(v, endpoints[0].get(k))

        # Not found
        endpoints = self.client.search_endpoints(id='blah!')
        self.assertEqual(0, len(endpoints))

        # Multiple matches
        endpoints = self.client.search_endpoints(
            filters={'region': 'region1'})
        # # test we are getting exactly 2 elements
        self.assertEqual(2, len(endpoints))

    @patch.object(OperatorCloud, 'keystone_client')
    def test_delete_endpoint(self, mock_keystone_client):
        mock_keystone_client.endpoints.list.return_value = \
            self.mock_ks_endpoints

        # Delete by id
        self.client.delete_endpoint(id='id2')
        mock_keystone_client.endpoints.delete.assert_called_with(id='id2')
