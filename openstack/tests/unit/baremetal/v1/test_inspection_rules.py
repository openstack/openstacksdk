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

from openstack.baremetal.v1 import inspection_rules
from openstack.tests.unit import base


FAKE = {
    "created_at": "2025-03-18T22:28:48.643434+11:11",
    "description": "BMC credentials",
    "phase": "main",
    "priority": 100,
    "sensitive": False,
    "actions": [
        {
            "op": "set-attribute",
            "args": {
                "path": "/properties/cpus",
                "value": "{inventory[cpu][count]}",
            },
        },
        {
            "op": "set-attribute",
            "args": {
                "path": "/properties/memory_mb",
                "value": "{inventory[memory][physical_mb]}",
            },
        },
        {
            "op": "set-attribute",
            "args": {
                "path": "/properties/cpu_arch",
                "value": "{inventory[cpu][architecture]}",
            },
        },
    ],
    "conditions": [
        {"op": "is-true", "args": {"value": "{inventory[cpu][count]}"}}
    ],
    "links": [
        {
            "href": "http://10.60.253.180:6385/v1/inspection_rules"
            "/783bf33a-a8e3-1e23-a645-1e95a1f95186",
            "rel": "self",
        },
        {
            "href": "http://10.60.253.180:6385/inspection_rules"
            "/783bf33a-a8e3-1e23-a645-1e95a1f95186",
            "rel": "bookmark",
        },
    ],
    "updated_at": None,
    "uuid": "783bf33a-a8e3-1e23-a645-1e95a1f95186",
}


class InspectionRules(base.TestCase):
    def test_basic(self):
        sot = inspection_rules.InspectionRule()
        self.assertIsNone(sot.resource_key)
        self.assertEqual('inspection_rules', sot.resources_key)
        self.assertEqual('/inspection_rules', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertEqual('PATCH', sot.commit_method)

    def test_instantiate(self):
        sot = inspection_rules.InspectionRule(**FAKE)
        self.assertEqual(FAKE['actions'], sot.actions)
        self.assertEqual(FAKE['description'], sot.description)
        self.assertEqual(FAKE['conditions'], sot.conditions)
        self.assertEqual(FAKE['created_at'], sot.created_at)
        self.assertEqual(FAKE['links'], sot.links)
        self.assertEqual(FAKE['phase'], sot.phase)
        self.assertEqual(FAKE['priority'], sot.priority)
        self.assertEqual(FAKE['sensitive'], sot.sensitive)
        self.assertEqual(FAKE['updated_at'], sot.updated_at)
        self.assertEqual(FAKE['uuid'], sot.id)
