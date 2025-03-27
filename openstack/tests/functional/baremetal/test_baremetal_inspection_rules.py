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
from openstack.tests.functional.baremetal import base


class TestBareMetalInspectionRule(base.BaseBaremetalTest):
    min_microversion = '1.96'

    def setUp(self):
        super().setUp()

    def test_baremetal_inspection_rule_create_get_delete(self):
        actions = [{"op": "set-attribute", "args": ["/driver", "idrac"]}]
        conditions = [
            {"op": "eq", "args": ["node:memory_mb", 4096], "multiple": "all"}
        ]
        inspection_rule = self.create_inspection_rule(
            actions=actions,
            conditions=conditions,
            description="Test inspection rule",
            phase="main",
            priority=100,
            sensitive=False,
        )
        loaded = self.conn.baremetal.get_inspection_rule(inspection_rule.id)
        self.assertEqual(loaded.id, inspection_rule.id)
        self.conn.baremetal.delete_inspection_rule(
            inspection_rule, ignore_missing=False
        )
        self.assertRaises(
            exceptions.NotFoundException,
            self.conn.baremetal.get_inspection_rule,
            inspection_rule.id,
        )

    def test_baremetal_inspection_rule_list(self):
        actions = [{"op": "set-attribute", "args": ["/driver", "idrac"]}]
        conditions = [
            {
                "op": "is-true",
                "args": ["{node.auto_discovered}"],
                "multiple": "any",
            }
        ]

        inspection_rule1 = self.create_inspection_rule(
            actions=actions,
            conditions=conditions,
            description="Test inspection rule 1",
        )
        inspection_rule2 = self.create_inspection_rule(
            actions=actions,
            conditions=conditions,
            description="Test inspection rule 2",
        )
        inspection_rules = self.conn.baremetal.inspection_rules()
        ids = [rule.id for rule in inspection_rules]
        self.assertIn(inspection_rule1.id, ids)
        self.assertIn(inspection_rule2.id, ids)

        inspection_rules_with_details = self.conn.baremetal.inspection_rules(
            details=True
        )
        for rule in inspection_rules_with_details:
            self.assertIsNotNone(rule.id)
            self.assertIsNotNone(rule.description)

        inspection_rule_with_fields = self.conn.baremetal.inspection_rules(
            fields=['uuid']
        )
        for rule in inspection_rule_with_fields:
            self.assertIsNotNone(rule.id)
            self.assertIsNone(rule.description)

    def test_baremetal_inspection_rule_list_update_delete(self):
        actions = [{"op": "set-attribute", "args": ["/driver", "idrac"]}]
        conditions = [
            {
                "op": "eq",
                "args": ["node:cpu_arch", "x86_64"],
                "multiple": "all",
            }
        ]
        inspection_rule = self.create_inspection_rule(
            actions=actions,
            conditions=conditions,
            description="Test inspection rule",
        )
        self.assertFalse(inspection_rule.extra)
        inspection_rule.description = 'Updated inspection rule'

        inspection_rule = self.conn.baremetal.update_inspection_rule(
            inspection_rule
        )
        self.assertEqual(
            'Updated inspection rule', inspection_rule.description
        )

        inspection_rule = self.conn.baremetal.get_inspection_rule(
            inspection_rule.id
        )

        self.conn.baremetal.delete_inspection_rule(
            inspection_rule.id, ignore_missing=False
        )

    def test_baremetal_inspection_rule_update(self):
        actions = [{"op": "set-attribute", "args": ["/driver", "idrac"]}]
        conditions = [
            {"op": "ge", "args": ["node:memory_mb", 4096], "multiple": "all"}
        ]
        inspection_rule = self.create_inspection_rule(
            actions=actions, conditions=conditions, phase="main", priority=100
        )
        inspection_rule.priority = 150

        inspection_rule = self.conn.baremetal.update_inspection_rule(
            inspection_rule
        )
        self.assertEqual(150, inspection_rule.priority)

        inspection_rule = self.conn.baremetal.get_inspection_rule(
            inspection_rule.id
        )
        self.assertEqual(150, inspection_rule.priority)

    def test_inspection_rule_patch(self):
        description = "BIOS configuration rule"
        actions = [
            {
                "op": "set-attribute",
                "args": ["/properties/capabilities", "boot_mode:uefi"],
            }
        ]
        conditions = [
            {
                "op": "is-true",
                "args": ["{node.auto_discovered}"],
                "multiple": "any",
            }
        ]
        inspection_rule = self.create_inspection_rule(
            actions=actions,
            conditions=conditions,
            description=description,
            sensitive=False,
        )

        updated_actions = [
            {
                "op": "set-attribute",
                "args": ["/driver", "fake"],
            }
        ]

        inspection_rule = self.conn.baremetal.patch_inspection_rule(
            inspection_rule,
            dict(path='/actions', op='add', value=updated_actions),
        )
        self.assertEqual(updated_actions, inspection_rule.actions)
        self.assertEqual(description, inspection_rule.description)

        inspection_rule = self.conn.baremetal.get_inspection_rule(
            inspection_rule.id
        )
        self.assertEqual(updated_actions, inspection_rule.actions)

    def test_inspection_rule_negative_non_existing(self):
        uuid = "bbb45f41-d4bc-4307-8d1d-32f95ce1e920"
        self.assertRaises(
            exceptions.NotFoundException,
            self.conn.baremetal.get_inspection_rule,
            uuid,
        )
        self.assertRaises(
            exceptions.NotFoundException,
            self.conn.baremetal.delete_inspection_rule,
            uuid,
            ignore_missing=False,
        )
        self.assertIsNone(self.conn.baremetal.delete_inspection_rule(uuid))
