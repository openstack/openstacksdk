# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
test_services
----------------------------------

Functional tests for `shade` service resource.
"""

import string
import random

from openstack.cloud.exc import OpenStackCloudException
from openstack.cloud.exc import OpenStackCloudUnavailableFeature
from openstack.tests.functional import base


class TestServices(base.KeystoneBaseFunctionalTest):

    service_attributes = ['id', 'name', 'type', 'description']

    def setUp(self):
        super(TestServices, self).setUp()

        # Generate a random name for services in this test
        self.new_service_name = 'test_' + ''.join(
            random.choice(string.ascii_lowercase) for _ in range(5))

        self.addCleanup(self._cleanup_services)

    def _cleanup_services(self):
        exception_list = list()
        for s in self.operator_cloud.list_services():
            if s['name'] is not None and \
                    s['name'].startswith(self.new_service_name):
                try:
                    self.operator_cloud.delete_service(name_or_id=s['id'])
                except Exception as e:
                    # We were unable to delete a service, let's try with next
                    exception_list.append(str(e))
                    continue
        if exception_list:
            # Raise an error: we must make users aware that something went
            # wrong
            raise OpenStackCloudException('\n'.join(exception_list))

    def test_create_service(self):
        service = self.operator_cloud.create_service(
            name=self.new_service_name + '_create', type='test_type',
            description='this is a test description')
        self.assertIsNotNone(service.get('id'))

    def test_update_service(self):
        ver = self.operator_cloud.config.get_api_version('identity')
        if ver.startswith('2'):
            # NOTE(SamYaple): Update service only works with v3 api
            self.assertRaises(OpenStackCloudUnavailableFeature,
                              self.operator_cloud.update_service,
                              'service_id', name='new name')
        else:
            service = self.operator_cloud.create_service(
                name=self.new_service_name + '_create', type='test_type',
                description='this is a test description', enabled=True)
            new_service = self.operator_cloud.update_service(
                service.id,
                name=self.new_service_name + '_update',
                description='this is an updated description',
                enabled=False
            )
            self.assertEqual(new_service.name,
                             self.new_service_name + '_update')
            self.assertEqual(new_service.description,
                             'this is an updated description')
            self.assertFalse(new_service.enabled)
            self.assertEqual(service.id, new_service.id)

    def test_list_services(self):
        service = self.operator_cloud.create_service(
            name=self.new_service_name + '_list', type='test_type')
        observed_services = self.operator_cloud.list_services()
        self.assertIsInstance(observed_services, list)
        found = False
        for s in observed_services:
            # Test all attributes are returned
            if s['id'] == service['id']:
                self.assertEqual(self.new_service_name + '_list',
                                 s.get('name'))
                self.assertEqual('test_type', s.get('type'))
                found = True
        self.assertTrue(found, msg='new service not found in service list!')

    def test_delete_service_by_name(self):
        # Test delete by name
        service = self.operator_cloud.create_service(
            name=self.new_service_name + '_delete_by_name',
            type='test_type')
        self.operator_cloud.delete_service(name_or_id=service['name'])
        observed_services = self.operator_cloud.list_services()
        found = False
        for s in observed_services:
            if s['id'] == service['id']:
                found = True
                break
        self.failUnlessEqual(False, found, message='service was not deleted!')

    def test_delete_service_by_id(self):
        # Test delete by id
        service = self.operator_cloud.create_service(
            name=self.new_service_name + '_delete_by_id',
            type='test_type')
        self.operator_cloud.delete_service(name_or_id=service['id'])
        observed_services = self.operator_cloud.list_services()
        found = False
        for s in observed_services:
            if s['id'] == service['id']:
                found = True
        self.failUnlessEqual(False, found, message='service was not deleted!')
