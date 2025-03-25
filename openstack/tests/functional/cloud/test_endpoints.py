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
test_endpoint
----------------------------------

Functional tests for endpoint resource.
"""

import random
import string

from openstack import exceptions
from openstack.tests.functional import base


class TestEndpoints(base.KeystoneBaseFunctionalTest):
    endpoint_attributes = [
        'id',
        'region',
        'publicurl',
        'internalurl',
        'service_id',
        'adminurl',
    ]

    def setUp(self):
        super().setUp()

        if not self.operator_cloud:
            self.skipTest("Operator cloud is required for this test")

        # Generate a random name for services and regions in this test
        self.new_item_name = 'test_' + ''.join(
            random.choice(string.ascii_lowercase) for _ in range(5)
        )

        self.addCleanup(self._cleanup_services)
        self.addCleanup(self._cleanup_endpoints)

    def _cleanup_endpoints(self):
        exception_list = list()
        for endpoint in self.operator_cloud.list_endpoints():
            if endpoint.get('region') is not None and endpoint[
                'region'
            ].startswith(self.new_item_name):
                try:
                    self.operator_cloud.delete_endpoint(id=endpoint['id'])
                except Exception as exc:
                    # We were unable to delete a service, let's try with next
                    exception_list.append(str(exc))
                    continue
        if exception_list:
            # Raise an error: we must make users aware that something went
            # wrong
            raise exceptions.SDKException('\n'.join(exception_list))

    def _cleanup_services(self):
        exception_list = list()
        for s in self.operator_cloud.list_services():
            if s['name'] is not None and s['name'].startswith(
                self.new_item_name
            ):
                try:
                    self.operator_cloud.delete_service(name_or_id=s['id'])
                except Exception as e:
                    # We were unable to delete a service, let's try with next
                    exception_list.append(str(e))
                    continue
        if exception_list:
            # Raise an error: we must make users aware that something went
            # wrong
            raise exceptions.SDKException('\n'.join(exception_list))

    def test_create_endpoint(self):
        service_name = self.new_item_name + '_create'

        region = list(self.operator_cloud.identity.regions())[0].id

        service = self.operator_cloud.create_service(
            name=service_name,
            type='test_type',
            description='this is a test description',
        )

        endpoints = self.operator_cloud.create_endpoint(
            service_name_or_id=service['id'],
            public_url='http://public.test/',
            internal_url='http://internal.test/',
            admin_url='http://admin.url/',
            region=region,
        )

        self.assertNotEqual([], endpoints)
        self.assertIsNotNone(endpoints[0].get('id'))

        # Test None parameters
        endpoints = self.operator_cloud.create_endpoint(
            service_name_or_id=service['id'],
            public_url='http://public.test/',
            region=region,
        )

        self.assertNotEqual([], endpoints)
        self.assertIsNotNone(endpoints[0].get('id'))

    def test_update_endpoint(self):
        # service operations require existing region. Do not test updating
        # region for now
        region = list(self.operator_cloud.identity.regions())[0].id

        service = self.operator_cloud.create_service(
            name='service1', type='test_type'
        )
        endpoint = self.operator_cloud.create_endpoint(
            service_name_or_id=service['id'],
            url='http://admin.url/',
            interface='admin',
            region=region,
            enabled=False,
        )[0]

        new_service = self.operator_cloud.create_service(
            name='service2', type='test_type'
        )
        new_endpoint = self.operator_cloud.update_endpoint(
            endpoint.id,
            service_name_or_id=new_service.id,
            url='http://public.url/',
            interface='public',
            region=region,
            enabled=True,
        )

        self.assertEqual(new_endpoint.url, 'http://public.url/')
        self.assertEqual(new_endpoint.interface, 'public')
        self.assertEqual(new_endpoint.region_id, region)
        self.assertEqual(new_endpoint.service_id, new_service.id)
        self.assertTrue(new_endpoint.is_enabled)

    def test_list_endpoints(self):
        service_name = self.new_item_name + '_list'

        region = list(self.operator_cloud.identity.regions())[0].id

        service = self.operator_cloud.create_service(
            name=service_name,
            type='test_type',
            description='this is a test description',
        )

        endpoints = self.operator_cloud.create_endpoint(
            service_name_or_id=service['id'],
            public_url='http://public.test/',
            internal_url='http://internal.test/',
            region=region,
        )

        observed_endpoints = self.operator_cloud.list_endpoints()
        found = False
        for e in observed_endpoints:
            # Test all attributes are returned
            for endpoint in endpoints:
                if e['id'] == endpoint['id']:
                    found = True
                    self.assertEqual(service['id'], e['service_id'])
                    if 'interface' in e:
                        if e['interface'] == 'internal':
                            self.assertEqual('http://internal.test/', e['url'])
                        elif e['interface'] == 'public':
                            self.assertEqual('http://public.test/', e['url'])
                    else:
                        self.assertEqual('http://public.test/', e['publicurl'])
                        self.assertEqual(
                            'http://internal.test/', e['internalurl']
                        )
                    self.assertEqual(region, e['region_id'])

        self.assertTrue(found, msg='new endpoint not found in endpoints list!')

    def test_delete_endpoint(self):
        service_name = self.new_item_name + '_delete'

        region = list(self.operator_cloud.identity.regions())[0].id

        service = self.operator_cloud.create_service(
            name=service_name,
            type='test_type',
            description='this is a test description',
        )

        endpoints = self.operator_cloud.create_endpoint(
            service_name_or_id=service['id'],
            public_url='http://public.test/',
            internal_url='http://internal.test/',
            region=region,
        )

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
        self.assertEqual(False, found, message='new endpoint was not deleted!')
