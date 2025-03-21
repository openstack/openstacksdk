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

import warnings

from testtools import matchers

from openstack import exceptions
from openstack.tests.unit import base


class CloudServices(base.TestCase):
    def setUp(self, cloud_config_fixture='clouds.yaml'):
        super().setUp(cloud_config_fixture)

    def get_mock_url(
        self,
        service_type='identity',
        interface='public',
        resource='services',
        append=None,
        base_url_append='v3',
        qs_elements=None,
    ):
        return super().get_mock_url(
            service_type,
            interface,
            resource,
            append,
            base_url_append,
            qs_elements,
        )

    def test_create_service_v3(self):
        service_data = self._get_service_data(
            name='a service', type='network', description='A test service'
        )
        self.register_uris(
            [
                dict(
                    method='POST',
                    uri=self.get_mock_url(),
                    status_code=200,
                    json=service_data.json_response_v3,
                    validate=dict(json={'service': service_data.json_request}),
                )
            ]
        )

        service = self.cloud.create_service(
            name=service_data.service_name,
            service_type=service_data.service_type,
            description=service_data.description,
        )
        self.assertThat(
            service.name, matchers.Equals(service_data.service_name)
        )
        self.assertThat(service.id, matchers.Equals(service_data.service_id))
        self.assertThat(
            service.description, matchers.Equals(service_data.description)
        )
        self.assertThat(
            service.type, matchers.Equals(service_data.service_type)
        )
        self.assert_calls()

    def test_update_service_v3(self):
        service_data = self._get_service_data(
            name='a service', type='network', description='A test service'
        )
        request = service_data.json_request.copy()
        request['enabled'] = False
        resp = service_data.json_response_v3.copy()
        resp['enabled'] = False
        request.pop('description')
        request.pop('name')
        request.pop('type')
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(append=[service_data.service_id]),
                    status_code=200,
                    json=service_data.json_request,
                ),
                dict(
                    method='PATCH',
                    uri=self.get_mock_url(append=[service_data.service_id]),
                    status_code=200,
                    json=resp,
                    validate=dict(json={'service': request}),
                ),
            ]
        )

        service = self.cloud.update_service(
            service_data.service_id, enabled=False
        )
        self.assertThat(
            service.name, matchers.Equals(service_data.service_name)
        )
        self.assertThat(service.id, matchers.Equals(service_data.service_id))
        self.assertThat(
            service.description, matchers.Equals(service_data.description)
        )
        self.assertThat(
            service.type, matchers.Equals(service_data.service_type)
        )
        self.assert_calls()

    def test_list_services(self):
        service_data = self._get_service_data()
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(),
                    status_code=200,
                    json={
                        'services': [service_data.json_response_v3['service']]
                    },
                )
            ]
        )
        services = self.cloud.list_services()
        self.assertThat(len(services), matchers.Equals(1))
        self.assertThat(
            services[0].id, matchers.Equals(service_data.service_id)
        )
        self.assertThat(
            services[0].name, matchers.Equals(service_data.service_name)
        )
        self.assertThat(
            services[0].type, matchers.Equals(service_data.service_type)
        )
        self.assert_calls()

    def test_get_service(self):
        service_data = self._get_service_data()
        service2_data = self._get_service_data()

        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(append=[service_data.service_id]),
                    status_code=200,
                    json=service_data.json_response_v3,
                ),
                # you can't retrieve by name
                dict(
                    method='GET',
                    uri=self.get_mock_url(append=[service_data.service_name]),
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(),
                    status_code=200,
                    json={
                        'services': [
                            service_data.json_response_v3['service'],
                            service2_data.json_response_v3['service'],
                        ]
                    },
                ),
                # you can't retrieve by name, especially if it doesn't exist
                dict(
                    method='GET',
                    uri=self.get_mock_url(append=['INVALID SERVICE']),
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        qs_elements=['name=INVALID SERVICE']
                    ),
                    json={'services': []},
                ),
            ]
        )

        # Search by id
        service = self.cloud.get_service(name_or_id=service_data.service_id)
        self.assertThat(service.id, matchers.Equals(service_data.service_id))

        # Search by name
        service = self.cloud.get_service(name_or_id=service_data.service_name)
        # test we are getting exactly 1 element
        self.assertThat(service.id, matchers.Equals(service_data.service_id))

        # Not found
        service = self.cloud.get_service(name_or_id='INVALID SERVICE')
        self.assertIs(None, service)

    def test_get_service__multiple_matches(self):
        service_a_data = self._get_service_data(type='type2')
        service_b_data = self._get_service_data(type='type2')

        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(),
                    status_code=200,
                    json={
                        'services': [
                            service_a_data.json_response_v3['service'],
                            service_b_data.json_response_v3['service'],
                        ]
                    },
                ),
            ]
        )

        # Multiple matches
        # test we are getting an Exception
        with warnings.catch_warnings(record=True):
            self.assertRaises(
                exceptions.SDKException,
                self.cloud.get_service,
                name_or_id=None,
                filters={'type': 'type2'},
            )
        self.assert_calls()

    def test_search_services(self):
        service_data = self._get_service_data()
        service2_data = self._get_service_data(type=service_data.service_type)
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(),
                    status_code=200,
                    json={
                        'services': [
                            service_data.json_response_v3['service'],
                            service2_data.json_response_v3['service'],
                        ]
                    },
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(),
                    status_code=200,
                    json={
                        'services': [
                            service_data.json_response_v3['service'],
                            service2_data.json_response_v3['service'],
                        ]
                    },
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(),
                    status_code=200,
                    json={
                        'services': [
                            service_data.json_response_v3['service'],
                            service2_data.json_response_v3['service'],
                        ]
                    },
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(),
                    status_code=200,
                    json={
                        'services': [
                            service_data.json_response_v3['service'],
                            service2_data.json_response_v3['service'],
                        ]
                    },
                ),
            ]
        )

        # Search by id
        services = self.cloud.search_services(
            name_or_id=service_data.service_id
        )
        # test we are getting exactly 1 element
        self.assertThat(len(services), matchers.Equals(1))
        self.assertThat(
            services[0].id, matchers.Equals(service_data.service_id)
        )

        # Search by name
        services = self.cloud.search_services(
            name_or_id=service_data.service_name
        )
        # test we are getting exactly 1 element
        self.assertThat(len(services), matchers.Equals(1))
        self.assertThat(
            services[0].name, matchers.Equals(service_data.service_name)
        )

        # Not found
        services = self.cloud.search_services(name_or_id='!INVALID!')
        self.assertThat(len(services), matchers.Equals(0))

        # Multiple matches
        services = self.cloud.search_services(
            filters={'type': service_data.service_type}
        )
        # test we are getting exactly 2 elements
        self.assertThat(len(services), matchers.Equals(2))
        self.assertThat(
            services[0].id, matchers.Equals(service_data.service_id)
        )
        self.assertThat(
            services[1].id, matchers.Equals(service2_data.service_id)
        )
        self.assert_calls()

    def test_delete_service(self):
        service_data = self._get_service_data()
        self.register_uris(
            [
                # you can't retrieve by name
                dict(
                    method='GET',
                    uri=self.get_mock_url(append=[service_data.service_name]),
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        qs_elements=[f'name={service_data.service_name}']
                    ),
                    status_code=200,
                    json={
                        'services': [service_data.json_response_v3['service']]
                    },
                ),
                dict(
                    method='DELETE',
                    uri=self.get_mock_url(append=[service_data.service_id]),
                    status_code=204,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(append=[service_data.service_id]),
                    status_code=200,
                    json=service_data.json_response_v3,
                ),
                dict(
                    method='DELETE',
                    uri=self.get_mock_url(append=[service_data.service_id]),
                    status_code=204,
                ),
            ]
        )

        # Delete by name
        self.cloud.delete_service(name_or_id=service_data.service_name)

        # Delete by id
        self.cloud.delete_service(service_data.service_id)

        self.assert_calls()
