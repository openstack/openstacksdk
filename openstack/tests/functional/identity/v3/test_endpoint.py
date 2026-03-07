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

from openstack.identity.v3 import endpoint as _endpoint
from openstack.tests.functional.identity.v3 import base


class TestEndpoint(base.BaseIdentityTest):
    def setUp(self):
        super().setUp()

        self.service_name = self.getUniqueString('service')
        self.service_type = self.getUniqueString('type')
        self.service = self.admin_identity_client.create_service(
            name=self.service_name,
            type=self.service_type,
        )
        self.addCleanup(
            self.admin_identity_client.delete_service, self.service
        )

        self.region_name = self.getUniqueString('region')
        self.region = self.admin_identity_client.create_region(
            name=self.region_name
        )
        self.addCleanup(self.admin_identity_client.delete_region, self.region)

        unique_base = self.getUniqueString('endpoint')
        self.test_url = f'https://{unique_base}.example.com/v1'
        self.updated_url = f'https://{unique_base}.example.com/v2'

    def _delete_endpoint(self, endpoint):
        ret = self.admin_identity_client.delete_endpoint(endpoint)
        self.assertIsNone(ret)

    def test_endpoint(self):
        # Create public endpoint
        public_endpoint = self.admin_identity_client.create_endpoint(
            service_id=self.service.id,
            interface='public',
            url=self.test_url,
            region_id=self.region.id,
            is_enabled=True,
        )
        self.addCleanup(self._delete_endpoint, public_endpoint)
        self.assertIsInstance(public_endpoint, _endpoint.Endpoint)
        self.assertIsNotNone(public_endpoint.id)
        self.assertEqual(self.service.id, public_endpoint.service_id)
        self.assertEqual('public', public_endpoint.interface)
        self.assertEqual(self.test_url, public_endpoint.url)
        self.assertEqual(self.region.id, public_endpoint.region_id)
        self.assertTrue(public_endpoint.is_enabled)

        # Create internal endpoint for filter testing
        internal_endpoint = self.admin_identity_client.create_endpoint(
            service_id=self.service.id,
            interface='internal',
            url=self.test_url,
            region_id=self.region.id,
        )
        self.addCleanup(self._delete_endpoint, internal_endpoint)
        self.assertIsInstance(internal_endpoint, _endpoint.Endpoint)
        self.assertIsNotNone(internal_endpoint.id)
        self.assertEqual('internal', internal_endpoint.interface)

        # Update public endpoint
        public_endpoint = self.admin_identity_client.update_endpoint(
            public_endpoint,
            url=self.updated_url,
            is_enabled=False,
        )
        self.assertIsInstance(public_endpoint, _endpoint.Endpoint)
        self.assertEqual(self.updated_url, public_endpoint.url)
        self.assertFalse(public_endpoint.is_enabled)

        # Get endpoint by ID
        public_endpoint = self.admin_identity_client.get_endpoint(
            public_endpoint.id
        )
        self.assertIsInstance(public_endpoint, _endpoint.Endpoint)
        self.assertEqual(self.updated_url, public_endpoint.url)
        self.assertFalse(public_endpoint.is_enabled)

        # Find endpoint
        found_endpoint = self.admin_identity_client.find_endpoint(
            public_endpoint.id
        )
        self.assertIsInstance(found_endpoint, _endpoint.Endpoint)
        self.assertEqual(public_endpoint.id, found_endpoint.id)

        # List endpoints
        endpoints = list(self.admin_identity_client.endpoints())
        self.assertIsInstance(endpoints[0], _endpoint.Endpoint)
        endpoint_ids = {ep.id for ep in endpoints}
        self.assertIn(public_endpoint.id, endpoint_ids)
        self.assertIn(internal_endpoint.id, endpoint_ids)

        # Test service filter
        service_endpoints = list(
            self.admin_identity_client.endpoints(service_id=self.service.id)
        )
        service_endpoint_ids = {ep.id for ep in service_endpoints}
        self.assertIn(public_endpoint.id, service_endpoint_ids)
        self.assertIn(internal_endpoint.id, service_endpoint_ids)

        # Test interface filter
        public_endpoints = list(
            self.admin_identity_client.endpoints(interface='public')
        )
        public_endpoint_ids = {ep.id for ep in public_endpoints}
        self.assertIn(public_endpoint.id, public_endpoint_ids)

        internal_endpoints = list(
            self.admin_identity_client.endpoints(interface='internal')
        )
        internal_endpoint_ids = {ep.id for ep in internal_endpoints}
        self.assertIn(internal_endpoint.id, internal_endpoint_ids)

        # Test region filter
        region_endpoints = list(
            self.admin_identity_client.endpoints(region_id=self.region.id)
        )
        region_endpoint_ids = {ep.id for ep in region_endpoints}
        self.assertIn(public_endpoint.id, region_endpoint_ids)
        self.assertIn(internal_endpoint.id, region_endpoint_ids)
