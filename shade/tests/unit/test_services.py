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
test_cloud_services
----------------------------------

Tests Keystone services commands.
"""

from mock import patch
import os_client_config
from shade import OpenStackCloudException
from shade import OperatorCloud
from shade.tests.fakes import FakeService
from shade.tests.unit import base


class CloudServices(base.TestCase):
    mock_services = [
        {'id': 'id1', 'name': 'service1', 'type': 'type1',
         'description': 'desc1'},
        {'id': 'id2', 'name': 'service2', 'type': 'type2',
         'description': 'desc2'},
        {'id': 'id3', 'name': 'service3', 'type': 'type2',
         'description': 'desc3'},
        {'id': 'id4', 'name': 'service4', 'type': 'type3',
         'description': 'desc4'}
    ]

    def setUp(self):
        super(CloudServices, self).setUp()
        config = os_client_config.OpenStackConfig()
        self.client = OperatorCloud(cloud_config=config.get_one_cloud(
            validate=False))
        self.mock_ks_services = [FakeService(**kwa) for kwa in
                                 self.mock_services]

    @patch.object(OperatorCloud, 'keystone_client')
    def test_create_service(self, mock_keystone_client):
        kwargs = {
            'name': 'a service',
            'service_type': 'network',
            'description': 'This is a test service'
        }

        self.client.create_service(**kwargs)
        mock_keystone_client.services.create.assert_called_with(**kwargs)

    @patch.object(OperatorCloud, 'keystone_client')
    def test_list_services(self, mock_keystone_client):
        mock_keystone_client.services.list.return_value = \
            self.mock_ks_services

        services = self.client.list_services()
        mock_keystone_client.services.list.assert_called_with()

        self.assertItemsEqual(self.mock_services, services)

    @patch.object(OperatorCloud, 'keystone_client')
    def test_get_service(self, mock_keystone_client):
        mock_keystone_client.services.list.return_value = \
            self.mock_ks_services

        # Search by id
        service = self.client.get_service(name_or_id='id4')
        # test we are getting exactly 1 element
        self.assertEqual(service, self.mock_services[3])

        # Search by name
        service = self.client.get_service(name_or_id='service2')
        # test we are getting exactly 1 element
        self.assertEqual(service, self.mock_services[1])

        # Not found
        service = self.client.get_service(name_or_id='blah!')
        self.assertIs(None, service)

        # Multiple matches
        # test we are getting an Exception
        self.assertRaises(OpenStackCloudException, self.client.get_service,
                          name_or_id=None, filters={'type': 'type2'})

    @patch.object(OperatorCloud, 'keystone_client')
    def test_search_services(self, mock_keystone_client):
        mock_keystone_client.services.list.return_value = \
            self.mock_ks_services

        # Search by id
        services = self.client.search_services(name_or_id='id4')
        # test we are getting exactly 1 element
        self.assertEqual(1, len(services))
        self.assertEqual(services, [self.mock_services[3]])

        # Search by name
        services = self.client.search_services(name_or_id='service2')
        # test we are getting exactly 1 element
        self.assertEqual(1, len(services))
        self.assertEqual(services, [self.mock_services[1]])

        # Not found
        services = self.client.search_services(name_or_id='blah!')
        self.assertEqual(0, len(services))

        # Multiple matches
        services = self.client.search_services(
            filters={'type': 'type2'})
        # test we are getting exactly 2 elements
        self.assertEqual(2, len(services))
        self.assertEqual(services, [self.mock_services[1],
                                    self.mock_services[2]])

    @patch.object(OperatorCloud, 'keystone_client')
    def test_delete_service(self, mock_keystone_client):
        mock_keystone_client.services.list.return_value = \
            self.mock_ks_services

        # Delete by name
        self.client.delete_service(name_or_id='service3')
        mock_keystone_client.services.delete.assert_called_with(id='id3')

        # Delete by id
        self.client.delete_service('id1')
        mock_keystone_client.services.delete.assert_called_with(id='id1')
