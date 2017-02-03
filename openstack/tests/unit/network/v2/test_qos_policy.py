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

import testtools
import uuid

from openstack.network.v2 import qos_policy

EXAMPLE = {
    'id': 'IDENTIFIER',
    'description': 'QoS policy description',
    'name': 'qos-policy-name',
    'shared': True,
    'tenant_id': '2',
    'rules': [uuid.uuid4().hex],
    'is_default': False
}


class TestQoSPolicy(testtools.TestCase):

    def test_basic(self):
        sot = qos_policy.QoSPolicy()
        self.assertEqual('policy', sot.resource_key)
        self.assertEqual('policies', sot.resources_key)
        self.assertEqual('/qos/policies', sot.base_path)
        self.assertEqual('network', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_get)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = qos_policy.QoSPolicy(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertTrue(sot.is_shared)
        self.assertEqual(EXAMPLE['tenant_id'], sot.project_id)
        self.assertEqual(EXAMPLE['rules'], sot.rules)
        self.assertEqual(EXAMPLE['is_default'], sot.is_default)
