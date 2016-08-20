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
from shade import _utils
from shade import meta
from shade import OpenStackCloudException
from shade.exc import OpenStackCloudUnavailableFeature
from shade import OperatorCloud
from shade.tests.fakes import FakeService
from shade.tests.unit import base


class CloudServices(base.TestCase):
    mock_services = [
        {'id': 'id1', 'name': 'service1', 'type': 'type1',
         'service_type': 'type1', 'description': 'desc1', 'enabled': True},
        {'id': 'id2', 'name': 'service2', 'type': 'type2',
         'service_type': 'type2', 'description': 'desc2', 'enabled': True},
        {'id': 'id3', 'name': 'service3', 'type': 'type2',
         'service_type': 'type2', 'description': 'desc3', 'enabled': True},
        {'id': 'id4', 'name': 'service4', 'type': 'type3',
         'service_type': 'type3', 'description': 'desc4', 'enabled': True}
    ]

    def setUp(self):
        super(CloudServices, self).setUp()
        self.mock_ks_services = [FakeService(**kwa) for kwa in
                                 self.mock_services]

    @patch.object(_utils, 'normalize_keystone_services')
    @patch.object(OperatorCloud, 'keystone_client')
    @patch.object(os_client_config.cloud_config.CloudConfig, 'get_api_version')
    def test_create_service_v2(self, mock_api_version, mock_keystone_client,
                               mock_norm):
        mock_api_version.return_value = '2.0'
        kwargs = {
            'name': 'a service',
            'type': 'network',
            'description': 'This is a test service'
        }

        self.op_cloud.create_service(**kwargs)
        kwargs['service_type'] = kwargs.pop('type')
        mock_keystone_client.services.create.assert_called_with(**kwargs)
        self.assertTrue(mock_norm.called)

    @patch.object(_utils, 'normalize_keystone_services')
    @patch.object(OperatorCloud, 'keystone_client')
    @patch.object(os_client_config.cloud_config.CloudConfig, 'get_api_version')
    def test_create_service_v3(self, mock_api_version, mock_keystone_client,
                               mock_norm):
        mock_api_version.return_value = '3'
        kwargs = {
            'name': 'a v3 service',
            'type': 'cinderv2',
            'description': 'This is a test service',
            'enabled': False
        }

        self.op_cloud.create_service(**kwargs)
        mock_keystone_client.services.create.assert_called_with(**kwargs)
        self.assertTrue(mock_norm.called)

    @patch.object(os_client_config.cloud_config.CloudConfig, 'get_api_version')
    def test_update_service_v2(self, mock_api_version):
        mock_api_version.return_value = '2.0'
        # NOTE(SamYaple): Update service only works with v3 api
        self.assertRaises(OpenStackCloudUnavailableFeature,
                          self.op_cloud.update_service,
                          'service_id', name='new name')

    @patch.object(_utils, 'normalize_keystone_services')
    @patch.object(OperatorCloud, 'keystone_client')
    @patch.object(os_client_config.cloud_config.CloudConfig, 'get_api_version')
    def test_update_service_v3(self, mock_api_version, mock_keystone_client,
                               mock_norm):
        mock_api_version.return_value = '3'
        kwargs = {
            'name': 'updated_name',
            'type': 'updated_type',
            'service_type': 'updated_type',
            'description': 'updated_name',
            'enabled': False
        }

        service_obj = FakeService(id='id1', **kwargs)
        mock_keystone_client.services.update.return_value = service_obj

        self.op_cloud.update_service('id1', **kwargs)
        del kwargs['service_type']
        mock_keystone_client.services.update.assert_called_once_with(
            service='id1', **kwargs
        )
        mock_norm.assert_called_once_with([meta.obj_to_dict(service_obj)])

    @patch.object(OperatorCloud, 'keystone_client')
    def test_list_services(self, mock_keystone_client):
        mock_keystone_client.services.list.return_value = \
            self.mock_ks_services
        services = self.op_cloud.list_services()
        mock_keystone_client.services.list.assert_called_with()
        self.assertItemsEqual(self.mock_services, services)

    @patch.object(OperatorCloud, 'keystone_client')
    def test_get_service(self, mock_keystone_client):
        mock_keystone_client.services.list.return_value = \
            self.mock_ks_services

        # Search by id
        service = self.op_cloud.get_service(name_or_id='id4')
        # test we are getting exactly 1 element
        self.assertEqual(service, self.mock_services[3])

        # Search by name
        service = self.op_cloud.get_service(name_or_id='service2')
        # test we are getting exactly 1 element
        self.assertEqual(service, self.mock_services[1])

        # Not found
        service = self.op_cloud.get_service(name_or_id='blah!')
        self.assertIs(None, service)

        # Multiple matches
        # test we are getting an Exception
        self.assertRaises(OpenStackCloudException, self.op_cloud.get_service,
                          name_or_id=None, filters={'type': 'type2'})

    @patch.object(OperatorCloud, 'keystone_client')
    def test_search_services(self, mock_keystone_client):
        mock_keystone_client.services.list.return_value = \
            self.mock_ks_services

        # Search by id
        services = self.op_cloud.search_services(name_or_id='id4')
        # test we are getting exactly 1 element
        self.assertEqual(1, len(services))
        self.assertEqual(services, [self.mock_services[3]])

        # Search by name
        services = self.op_cloud.search_services(name_or_id='service2')
        # test we are getting exactly 1 element
        self.assertEqual(1, len(services))
        self.assertEqual(services, [self.mock_services[1]])

        # Not found
        services = self.op_cloud.search_services(name_or_id='blah!')
        self.assertEqual(0, len(services))

        # Multiple matches
        services = self.op_cloud.search_services(
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
        self.op_cloud.delete_service(name_or_id='service3')
        mock_keystone_client.services.delete.assert_called_with(id='id3')

        # Delete by id
        self.op_cloud.delete_service('id1')
        mock_keystone_client.services.delete.assert_called_with(id='id1')
