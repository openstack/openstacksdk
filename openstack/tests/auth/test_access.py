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
import testtools

from openstack.auth import access
from openstack.tests.auth import common


class TestAccessInfo(testtools.TestCase):
    def test_is_valid(self):
        v2body = common.TEST_RESPONSE_DICT_V2
        v3body = common.TEST_RESPONSE_DICT_V3
        self.assertTrue(access.AccessInfoV2.is_valid(v2body))
        self.assertFalse(access.AccessInfoV2.is_valid(v3body))
        self.assertFalse(access.AccessInfoV3.is_valid(v2body))
        self.assertTrue(access.AccessInfoV3.is_valid(v3body))

    def test_factory_v2(self):
        sot = access.AccessInfo.factory(body=common.TEST_RESPONSE_DICT_V2)

        self.assertTrue(isinstance(sot, access.AccessInfoV2))
        self.assertFalse(sot.will_expire_soon())
        self.assertTrue(sot.has_service_catalog())
        self.assertEqual(common.TEST_TOKEN, sot.auth_token)
        self.assertEqual(common.TEST_EXPIRES, str(sot.expires))
        self.assertEqual(None, sot.username)
        self.assertEqual(common.TEST_USER_ID, sot.user_id)
        self.assertEqual('default', sot.user_domain_id)
        self.assertEqual('Default', sot.user_domain_name)
        self.assertEqual([], sot.role_names)
        self.assertEqual(None, sot.domain_id)
        self.assertEqual(None, sot.domain_name)
        self.assertEqual(None, sot.project_name)
        self.assertEqual(None, sot.tenant_name)
        self.assertTrue(sot.project_scoped)
        self.assertFalse(sot.domain_scoped)
        self.assertEqual(None, sot.trust_id)
        self.assertFalse(sot.trust_scoped)
        self.assertEqual(common.TEST_TENANT_ID, sot.project_id)
        self.assertEqual(common.TEST_TENANT_ID, sot.tenant_id)
        self.assertEqual('default', sot.project_domain_id)
        self.assertEqual('Default', sot.project_domain_name)
        self.assertEqual('v2.0', sot.version)

    def test_factory_v3(self):
        response = mock.Mock()
        response.headers = {'X-Subject-Token': common.TEST_TOKEN}
        sot = access.AccessInfo.factory(body=common.TEST_RESPONSE_DICT_V3,
                                        resp=response)

        self.assertTrue(isinstance(sot, access.AccessInfoV3))
        self.assertFalse(sot.will_expire_soon())
        self.assertTrue(sot.has_service_catalog())
        self.assertEqual(common.TEST_TOKEN, sot.auth_token)
        self.assertEqual(common.TEST_EXPIRES, str(sot.expires))
        self.assertEqual(common.TEST_USER, sot.username)
        self.assertEqual(common.TEST_USER_ID, sot.user_id)
        self.assertEqual(common.TEST_DOMAIN_ID, sot.user_domain_id)
        self.assertEqual(common.TEST_DOMAIN_NAME, sot.user_domain_name)
        self.assertEqual([], sot.role_names)
        self.assertEqual(None, sot.domain_id)
        self.assertEqual(None, sot.domain_name)
        self.assertEqual(common.TEST_PROJECT_NAME, sot.project_name)
        self.assertEqual(common.TEST_PROJECT_NAME, sot.tenant_name)
        self.assertTrue(sot.project_scoped)
        self.assertFalse(sot.domain_scoped)
        self.assertEqual(None, sot.trust_id)
        self.assertFalse(sot.trust_scoped)
        self.assertEqual(common.TEST_PROJECT_ID, sot.project_id)
        self.assertEqual(common.TEST_PROJECT_ID, sot.tenant_id)
        self.assertEqual(common.TEST_DOMAIN_ID, sot.project_domain_id)
        self.assertEqual(common.TEST_DOMAIN_NAME, sot.project_domain_name)
        self.assertEqual('v3', sot.version)

    def test_factory_raises(self):
        self.assertRaises(NotImplementedError, access.AccessInfo.factory,
                          body={})
