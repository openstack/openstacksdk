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

from openstack.identity.v3 import endpoint_group as _endpoint_group
from openstack.tests.functional.identity.v3 import base


class TestEndpointGroup(base.BaseIdentityTest):
    def setUp(self):
        super().setUp()

        self.endpoint_group_name = self.getUniqueString('endpoint_group')
        self.endpoint_group_description = self.getUniqueString(
            'endpoint_group'
        )

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

        # Create public endpoint
        self.public_endpoint = self.admin_identity_client.create_endpoint(
            service_id=self.service.id,
            interface='public',
            url=self.test_url,
            region_id=self.region.id,
            is_enabled=True,
        )
        self.addCleanup(
            self.admin_identity_client.delete_endpoint, self.public_endpoint
        )

        # Create internal endpoint for filter testing
        self.internal_endpoint = self.admin_identity_client.create_endpoint(
            service_id=self.service.id,
            interface='internal',
            url=self.test_url,
            region_id=self.region.id,
        )
        self.addCleanup(
            self.admin_identity_client.delete_endpoint, self.internal_endpoint
        )

        self.initial_filters = {
            'interface': 'internal',
        }
        self.filters = {
            'interface': 'public',
            'service_id': self.service.id,
            'region_id': self.region.id,
        }

    def _delete_endpoint_group(self, endpoint_group):
        ret = self.admin_identity_client.delete_endpoint_group(endpoint_group)
        self.assertIsNone(ret)

    def test_endpoint_group(self):
        # Create endpoint group
        endpoint_group = self.admin_identity_client.create_endpoint_group(
            name=self.endpoint_group_name, filters=self.initial_filters
        )
        self.addCleanup(self._delete_endpoint_group, endpoint_group)
        self.assertIsInstance(endpoint_group, _endpoint_group.EndpointGroup)
        self.assertIsNotNone(endpoint_group.id)
        self.assertEqual(self.endpoint_group_name, endpoint_group.name)
        self.assertDictEqual(self.initial_filters, endpoint_group.filters)
        self.assertIsNone(endpoint_group.description)

        # Update endpoint group
        endpoint_group = self.admin_identity_client.update_endpoint_group(
            endpoint_group,
            description=self.endpoint_group_description,
            filters=self.filters,
        )
        self.assertIsInstance(endpoint_group, _endpoint_group.EndpointGroup)
        self.assertEqual(self.endpoint_group_name, endpoint_group.name)
        self.assertEqual(
            self.endpoint_group_description, endpoint_group.description
        )
        self.assertDictEqual(self.filters, endpoint_group.filters)

        # Get endpoint group by ID
        endpoint_group = self.admin_identity_client.get_endpoint_group(
            endpoint_group.id
        )
        self.assertIsInstance(endpoint_group, _endpoint_group.EndpointGroup)
        self.assertEqual(self.endpoint_group_name, endpoint_group.name)
        self.assertEqual(
            self.endpoint_group_description, endpoint_group.description
        )
        self.assertDictEqual(self.filters, endpoint_group.filters)

        # Find endpoint group
        found_endpoint_group = self.admin_identity_client.find_endpoint_group(
            endpoint_group.id, ignore_missing=False
        )
        self.assertIsInstance(
            found_endpoint_group, _endpoint_group.EndpointGroup
        )
        self.assertEqual(endpoint_group.id, found_endpoint_group.id)

        # Check filtered endpoints in endpoint group
        filtered_endpoints = list(
            self.admin_identity_client.endpoint_group_endpoints(endpoint_group)
        )
        endpoint_ids = {e.id for e in filtered_endpoints}
        self.assertIn(self.public_endpoint.id, endpoint_ids)
        self.assertNotIn(self.internal_endpoint.id, endpoint_ids)

        # List endpoint groups
        endpoint_groups = list(self.admin_identity_client.endpoint_groups())
        self.assertIsInstance(
            endpoint_groups[0], _endpoint_group.EndpointGroup
        )
        endpoint_group_ids = {eg.id for eg in endpoint_groups}
        self.assertIn(endpoint_group.id, endpoint_group_ids)

        # Test name filter
        endpoint_groups = list(
            self.admin_identity_client.endpoint_groups(
                name=endpoint_group.name
            )
        )
        self.assertIsInstance(
            endpoint_groups[0], _endpoint_group.EndpointGroup
        )
        endpoint_group_ids = {eg.id for eg in endpoint_groups}
        self.assertIn(endpoint_group.id, endpoint_group_ids)
