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
# See the License for the specific language governing permissions and
# limitations under the License.

import mock

import shade
from shade.tests.unit import base
from shade.tests import fakes


domain_obj = fakes.FakeIdentityDomain(
    id='1',
    name='a-domain',
    description='A wonderful keystone domain',
    enabled=True,
)


class TestIdentityDomains(base.TestCase):

    def setUp(self):
        super(TestIdentityDomains, self).setUp()
        self.cloud = shade.operator_cloud(validate=False)

    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_list_identity_domains(self, mock_keystone):
        self.cloud.list_identity_domains()
        self.assertTrue(mock_keystone.domains.list.called)

    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_get_identity_domain(self, mock_keystone):
        mock_keystone.domains.get.return_value = domain_obj
        domain = self.cloud.get_identity_domain(domain_id='1234')
        self.assertFalse(mock_keystone.domains.list.called)
        self.assertTrue(mock_keystone.domains.get.called)
        self.assertEqual(domain['name'], 'a-domain')
