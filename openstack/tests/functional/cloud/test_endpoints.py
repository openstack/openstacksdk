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
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
#
# See the License for the specific language governing permissions and
# limitations under the License.

"""
test_endpoint
----------------------------------

Functional tests for `shade` endpoint resource.
"""

import string
import random

from openstack.cloud.exc import OpenStackCloudException
from openstack.cloud.exc import OpenStackCloudUnavailableFeature
from openstack.tests.functional.cloud import base


class TestEndpoints(base.KeystoneBaseFunctionalTestCase):

    endpoint_attributes = ['id', 'region', 'publicurl', 'internalurl',
                           'service_id', 'adminurl']

    def setUp(self):
        super(TestEndpoints, self).setUp()

        # Generate a random name for services and regions in this test
        self.new_item_name = 'test_' + ''.join(
            random.choice(string.ascii_lowercase) for _ in range(5))

        self.addCleanup(self._cleanup_services)
        self.addCleanup(self._cleanup_endpoints)

    def _cleanup_endpoints(self):
        exception_list = list()
        for e in self.operator_cloud.list_endpoints():
            if e.get('region') is not None and \
                    e['region'].startswith(self.new_item_name):
                try:
                    self.operator_cloud.delete_endpoint(id=e['id'])
                except Exception as e:
                    # We were unable to delete a service, let's try with next
                    exception_list.append(str(e))
                    continue
        if exception_list:
            # Raise an error: we must make users aware that something went
            # wrong
            raise OpenStackCloudException('\n'.join(exception_list))

    def _cleanup_services(self):
        exception_list = list()
        for s in self.operator_cloud.list_services():
            if s['name'] is not None and \
                    s['name'].startswith(self.new_item_name):
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

    def test_create_endpoint(self):
        service_name = self.new_item_name + '_create'

        service = self.operator_cloud.create_service(
            name=service_name, type='test_type',
            description='this is a test description')

        endpoints = self.operator_cloud.create_endpoint(
            service_name_or_id=service['id'],
            public_url='http://public.test/',
            internal_url='http://internal.test/',
            admin_url='http://admin.url/',
            region=service_name)

        self.assertNotEqual([], endpoints)
        self.assertIsNotNone(endpoints[0].get('id'))

        # Test None parameters
        endpoints = self.operator_cloud.create_endpoint(
            service_name_or_id=service['id'],
            public_url='http://public.test/',
            region=service_name)

        self.assertNotEqual([], endpoints)
        self.assertIsNotNone(endpoints[0].get('id'))

    def test_update_endpoint(self):
        ver = self.operator_cloud.config.get_api_version('identity')
        if ver.startswith('2'):
            # NOTE(SamYaple): Update endpoint only works with v3 api
            self.assertRaises(OpenStackCloudUnavailableFeature,
                              self.operator_cloud.update_endpoint,
                              'endpoint_id1')
        else:
            service = self.operator_cloud.create_service(
                name='service1', type='test_type')
            endpoint = self.operator_cloud.create_endpoint(
                service_name_or_id=service['id'],
                url='http://admin.url/',
                interface='admin',
                region='orig_region',
                enabled=False)[0]

            new_service = self.operator_cloud.create_service(
                name='service2', type='test_type')
            new_endpoint = self.operator_cloud.update_endpoint(
                endpoint.id,
                service_name_or_id=new_service.id,
                url='http://public.url/',
                interface='public',
                region='update_region',
                enabled=True)

            self.assertEqual(new_endpoint.url, 'http://public.url/')
            self.assertEqual(new_endpoint.interface, 'public')
            self.assertEqual(new_endpoint.region, 'update_region')
            self.assertEqual(new_endpoint.service_id, new_service.id)
            self.assertTrue(new_endpoint.enabled)

    def test_list_endpoints(self):
        service_name = self.new_item_name + '_list'

        service = self.operator_cloud.create_service(
            name=service_name, type='test_type',
            description='this is a test description')

        endpoints = self.operator_cloud.create_endpoint(
            service_name_or_id=service['id'],
            public_url='http://public.test/',
            internal_url='http://internal.test/',
            region=service_name)

        observed_endpoints = self.operator_cloud.list_endpoints()
        found = False
        for e in observed_endpoints:
            # Test all attributes are returned
            for endpoint in endpoints:
                if e['id'] == endpoint['id']:
                    found = True
                    self.assertEqual(service['id'], e['service_id'])
                    if 'interface' in e:
                        if 'interface' == 'internal':
                            self.assertEqual('http://internal.test/', e['url'])
                        elif 'interface' == 'public':
                            self.assertEqual('http://public.test/', e['url'])
                    else:
                        self.assertEqual('http://public.test/',
                                         e['publicurl'])
                        self.assertEqual('http://internal.test/',
                                         e['internalurl'])
                    self.assertEqual(service_name, e['region'])

        self.assertTrue(found, msg='new endpoint not found in endpoints list!')

    def test_delete_endpoint(self):
        service_name = self.new_item_name + '_delete'

        service = self.operator_cloud.create_service(
            name=service_name, type='test_type',
            description='this is a test description')

        endpoints = self.operator_cloud.create_endpoint(
            service_name_or_id=service['id'],
            public_url='http://public.test/',
            internal_url='http://internal.test/',
            region=service_name)

        self.assertNotEqual([], endpoints)
        for endpoint in endpoints:
            self.operator_cloud.delete_endpoint(endpoint['id'])

        observed_endpoints = self.operator_cloud.list_endpoints()
        found = False
        for e in observed_endpoints:
            for endpoint in endpoints:
                if e['id'] == endpoint['id']:
                    found = True
                    break
        self.failUnlessEqual(
            False, found, message='new endpoint was not deleted!')
