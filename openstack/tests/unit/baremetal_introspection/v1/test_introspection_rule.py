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

from openstack.baremetal_introspection.v1 import introspection_rule
from openstack.tests.unit import base

FAKE = {
    "actions": [
        {
            "action": "set-attribute",
            "path": "driver_info/deploy_kernel",
            "value": "8fd65-c97b-4d00-aa8b-7ed166a60971",
        },
        {
            "action": "set-attribute",
            "path": "driver_info/deploy_ramdisk",
            "value": "09e5420c-6932-4199-996e-9485c56b3394",
        },
    ],
    "conditions": [
        {
            "field": "node://driver_info.deploy_ramdisk",
            "invert": False,
            "multiple": "any",
            "op": "is-empty",
        },
        {
            "field": "node://driver_info.deploy_kernel",
            "invert": False,
            "multiple": "any",
            "op": "is-empty",
        },
    ],
    "description": "Set deploy info if not already set on node",
    "links": [
        {
            "href": "/v1/rules/7459bf7c-9ff9-43a8-ba9f-48542ecda66c",
            "rel": "self",
        }
    ],
    "uuid": "7459bf7c-9ff9-43a8-ba9f-48542ecda66c",
    "scope": "",
}


class TestIntrospectionRule(base.TestCase):
    def test_basic(self):
        sot = introspection_rule.IntrospectionRule()
        self.assertIsNone(sot.resource_key)
        self.assertEqual('rules', sot.resources_key)
        self.assertEqual('/rules', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertEqual('POST', sot.create_method)

    def test_instantiate(self):
        sot = introspection_rule.IntrospectionRule(**FAKE)
        self.assertEqual(FAKE['conditions'], sot.conditions)
        self.assertEqual(FAKE['actions'], sot.actions)
        self.assertEqual(FAKE['description'], sot.description)
        self.assertEqual(FAKE['uuid'], sot.id)
        self.assertEqual(FAKE['scope'], sot.scope)
