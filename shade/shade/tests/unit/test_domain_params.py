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

import mock

import munch

import shade
from shade import exc
from shade.tests.unit import base


class TestDomainParams(base.TestCase):

    @mock.patch.object(shade.OpenStackCloud, '_is_client_version')
    @mock.patch.object(shade.OpenStackCloud, 'get_project')
    def test_identity_params_v3(self, mock_get_project,
                                mock_is_client_version):
        mock_get_project.return_value = munch.Munch(id=1234)
        mock_is_client_version.return_value = True

        ret = self.cloud._get_identity_params(domain_id='5678', project='bar')
        self.assertIn('default_project_id', ret)
        self.assertEqual(ret['default_project_id'], 1234)
        self.assertIn('domain_id', ret)
        self.assertEqual(ret['domain_id'], '5678')

    @mock.patch.object(shade.OpenStackCloud, '_is_client_version')
    @mock.patch.object(shade.OpenStackCloud, 'get_project')
    def test_identity_params_v3_no_domain(
            self, mock_get_project, mock_is_client_version):
        mock_get_project.return_value = munch.Munch(id=1234)
        mock_is_client_version.return_value = True

        self.assertRaises(
            exc.OpenStackCloudException,
            self.cloud._get_identity_params,
            domain_id=None, project='bar')

    @mock.patch.object(shade.OpenStackCloud, '_is_client_version')
    @mock.patch.object(shade.OpenStackCloud, 'get_project')
    def test_identity_params_v2(self, mock_get_project,
                                mock_is_client_version):
        mock_get_project.return_value = munch.Munch(id=1234)
        mock_is_client_version.return_value = False

        ret = self.cloud._get_identity_params(domain_id='foo', project='bar')
        self.assertIn('tenant_id', ret)
        self.assertEqual(ret['tenant_id'], 1234)
        self.assertNotIn('domain', ret)

    @mock.patch.object(shade.OpenStackCloud, '_is_client_version')
    @mock.patch.object(shade.OpenStackCloud, 'get_project')
    def test_identity_params_v2_no_domain(self, mock_get_project,
                                          mock_is_client_version):
        mock_get_project.return_value = munch.Munch(id=1234)
        mock_is_client_version.return_value = False

        ret = self.cloud._get_identity_params(domain_id=None, project='bar')
        api_calls = [mock.call('identity', 3), mock.call('identity', 3)]
        mock_is_client_version.assert_has_calls(api_calls)
        self.assertIn('tenant_id', ret)
        self.assertEqual(ret['tenant_id'], 1234)
        self.assertNotIn('domain', ret)
