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

from openstack.cloud import exc
from openstack.tests.unit import base


class TestDomainParams(base.TestCase):

    def test_identity_params_v3(self):
        project_data = self._get_project_data(v3=True)
        self.register_uris([
            dict(method='GET',
                 uri='https://identity.example.com/v3/projects',
                 json=dict(projects=[project_data.json_response['project']]))
        ])

        ret = self.cloud._get_identity_params(
            domain_id='5678', project=project_data.project_name)
        self.assertIn('default_project_id', ret)
        self.assertEqual(ret['default_project_id'], project_data.project_id)
        self.assertIn('domain_id', ret)
        self.assertEqual(ret['domain_id'], '5678')

        self.assert_calls()

    def test_identity_params_v3_no_domain(self):
        project_data = self._get_project_data(v3=True)

        self.assertRaises(
            exc.OpenStackCloudException,
            self.cloud._get_identity_params,
            domain_id=None, project=project_data.project_name)

        self.assert_calls()

    def test_identity_params_v2(self):
        self.use_keystone_v2()
        project_data = self._get_project_data(v3=False)
        self.register_uris([
            dict(method='GET',
                 uri='https://identity.example.com/v2.0/tenants',
                 json=dict(tenants=[project_data.json_response['tenant']]))
        ])

        ret = self.cloud._get_identity_params(
            domain_id='foo', project=project_data.project_name)
        self.assertIn('tenant_id', ret)
        self.assertEqual(ret['tenant_id'], project_data.project_id)
        self.assertNotIn('domain', ret)

        self.assert_calls()

    def test_identity_params_v2_no_domain(self):
        self.use_keystone_v2()
        project_data = self._get_project_data(v3=False)
        self.register_uris([
            dict(method='GET',
                 uri='https://identity.example.com/v2.0/tenants',
                 json=dict(tenants=[project_data.json_response['tenant']]))
        ])

        ret = self.cloud._get_identity_params(
            domain_id=None, project=project_data.project_name)
        self.assertIn('tenant_id', ret)
        self.assertEqual(ret['tenant_id'], project_data.project_id)
        self.assertNotIn('domain', ret)

        self.assert_calls()
