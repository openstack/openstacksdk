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

from openstack import exceptions
from openstack.tests.unit import base


class TestDomainParams(base.TestCase):
    def get_mock_url(
        self,
        service_type='identity',
        interface='public',
        resource='projects',
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

    def test_identity_params_v3(self):
        project_data = self._get_project_data(v3=True)
        self.register_uris(
            [
                # can't retrieve by name
                dict(
                    method='GET',
                    uri=self.get_mock_url(append=[project_data.project_name]),
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        qs_elements=[f'name={project_data.project_name}']
                    ),
                    json=dict(
                        projects=[project_data.json_response['project']]
                    ),
                ),
            ]
        )

        ret = self.cloud._get_identity_params(
            domain_id='5678', project=project_data.project_name
        )
        self.assertIn('default_project_id', ret)
        self.assertEqual(ret['default_project_id'], project_data.project_id)
        self.assertIn('domain_id', ret)
        self.assertEqual(ret['domain_id'], '5678')

        self.assert_calls()

    def test_identity_params_v3_no_domain(self):
        project_data = self._get_project_data(v3=True)

        self.assertRaises(
            exceptions.SDKException,
            self.cloud._get_identity_params,
            domain_id=None,
            project=project_data.project_name,
        )

        self.assert_calls()
