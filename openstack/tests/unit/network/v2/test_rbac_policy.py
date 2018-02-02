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

from openstack.tests.unit import base

from openstack.network.v2 import rbac_policy

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'action': 'access_as_shared',
    'object_id': IDENTIFIER,
    'object_type': 'network',
    'target_tenant': '10',
    'tenant_id': '5',
}


class TestRBACPolicy(base.TestCase):

    def test_basic(self):
        sot = rbac_policy.RBACPolicy()
        self.assertEqual('rbac_policy', sot.resource_key)
        self.assertEqual('rbac_policies', sot.resources_key)
        self.assertEqual('/rbac-policies', sot.base_path)
        self.assertEqual('network', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_get)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = rbac_policy.RBACPolicy(**EXAMPLE)
        self.assertEqual(EXAMPLE['action'], sot.action)
        self.assertEqual(EXAMPLE['object_id'], sot.object_id)
        self.assertEqual(EXAMPLE['object_type'], sot.object_type)
        self.assertEqual(EXAMPLE['target_tenant'], sot.target_project_id)
        self.assertEqual(EXAMPLE['tenant_id'], sot.project_id)
