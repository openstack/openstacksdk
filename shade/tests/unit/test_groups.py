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
# See the License for the specific language governing permissions and
# limitations under the License.

from shade.tests.unit import base


class TestGroups(base.RequestsMockTestCase):
    def setUp(self, cloud_config_fixture='clouds.yaml'):
        super(TestGroups, self).setUp(
            cloud_config_fixture=cloud_config_fixture)
        self.addCleanup(self.assert_calls)

    def get_mock_url(self, service_type='identity', interface='admin',
                     resource='groups', append=None, base_url_append='v3'):
        return super(TestGroups, self).get_mock_url(
            service_type='identity', interface='admin', resource=resource,
            append=append, base_url_append=base_url_append)

    def test_list_groups(self):
        group_data = self._get_group_data()
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(),
                 status_code=200,
                 json={'groups': [group_data.json_response['group']]})
        ])
        self.op_cloud.list_groups()

    def test_get_group(self):
        group_data = self._get_group_data()
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(),
                 status_code=200,
                 json={'groups': [group_data.json_response['group']]}),
        ])
        self.op_cloud.get_group(group_data.group_id)

    def test_delete_group(self):
        group_data = self._get_group_data()
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(),
                 status_code=200,
                 json={'groups': [group_data.json_response['group']]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(append=[group_data.group_id]),
                 status_code=204),
        ])
        self.assertTrue(self.op_cloud.delete_group(group_data.group_id))

    def test_create_group(self):
        domain_data = self._get_domain_data()
        group_data = self._get_group_data(domain_id=domain_data.domain_id)
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(resource='domains',
                                       append=[domain_data.domain_id]),
                 status_code=200,
                 json=domain_data.json_response),
            dict(method='POST',
                 uri=self.get_mock_url(),
                 status_code=200,
                 json=group_data.json_response,
                 validate=dict(json=group_data.json_request))
        ])
        self.op_cloud.create_group(
            name=group_data.group_name, description=group_data.description,
            domain=group_data.domain_id)

    def test_update_group(self):
        group_data = self._get_group_data()
        # Domain ID is not sent
        group_data.json_request['group'].pop('domain_id')
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(),
                 status_code=200,
                 json={'groups': [group_data.json_response['group']]}),
            dict(method='PATCH',
                 uri=self.get_mock_url(append=[group_data.group_id]),
                 status_code=200,
                 json=group_data.json_response,
                 validate=dict(json=group_data.json_request))
        ])
        self.op_cloud.update_group(group_data.group_id, group_data.group_name,
                                   group_data.description)
