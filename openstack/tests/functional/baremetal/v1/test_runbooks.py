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
from openstack.tests.functional.baremetal.v1 import base


class TestBareMetalRunbook(base.BaseBaremetalTest):
    min_microversion = '1.92'

    def test_baremetal_runbook_create_get_delete(self):
        steps = [
            {
                "interface": "bios",
                "step": "apply_configuration",
                "args": {
                    "settings": [{"name": "LogicalProc", "value": "Enabled"}]
                },
                "order": 150,
            }
        ]
        runbook = self.create_runbook(name='CUSTOM_RUNBOOK', steps=steps)
        loaded = self.operator_cloud.baremetal.get_runbook(runbook.id)
        self.assertEqual(loaded.id, runbook.id)
        self.operator_cloud.baremetal.delete_runbook(
            runbook, ignore_missing=False
        )
        self.assertRaises(
            exceptions.NotFoundException,
            self.operator_cloud.baremetal.get_runbook,
            runbook.id,
        )

    def test_baremetal_runbook_list(self):
        steps = [
            {
                "interface": "bios",
                "step": "apply_configuration",
                "args": {
                    "settings": [{"name": "LogicalProc", "value": "Enabled"}]
                },
                "order": 150,
            }
        ]

        runbook1 = self.create_runbook(name='CUSTOM_RUNBOOK1', steps=steps)
        runbook2 = self.create_runbook(name='CUSTOM_RUNBOOK2', steps=steps)
        runbooks = self.operator_cloud.baremetal.runbooks()
        ids = [runbook.id for runbook in runbooks]
        self.assertIn(runbook1.id, ids)
        self.assertIn(runbook2.id, ids)

        runbooks_with_details = self.operator_cloud.baremetal.runbooks(
            details=True
        )
        for runbook in runbooks_with_details:
            self.assertIsNotNone(runbook.id)
            self.assertIsNotNone(runbook.name)

        runbook_with_fields = self.operator_cloud.baremetal.runbooks(
            fields=['uuid']
        )
        for runbook in runbook_with_fields:
            self.assertIsNotNone(runbook.id)
            self.assertIsNone(runbook.name)

    def test_baremetal_runbook_list_update_delete(self):
        steps = [
            {
                "interface": "bios",
                "step": "apply_configuration",
                "args": {
                    "settings": [{"name": "LogicalProc", "value": "Enabled"}]
                },
                "order": 150,
            }
        ]
        runbook = self.create_runbook(name='CUSTOM_RUNBOOK4', steps=steps)
        self.assertFalse(runbook.extra)
        runbook.extra = {'answer': 42}

        runbook = self.operator_cloud.baremetal.update_runbook(runbook)
        self.assertEqual({'answer': 42}, runbook.extra)

        runbook = self.operator_cloud.baremetal.get_runbook(runbook.id)

        self.operator_cloud.baremetal.delete_runbook(
            runbook.id, ignore_missing=False
        )

    def test_baremetal_runbook_update(self):
        steps = [
            {
                "interface": "bios",
                "step": "apply_configuration",
                "args": {
                    "settings": [{"name": "LogicalProc", "value": "Enabled"}]
                },
                "order": 150,
            }
        ]
        runbook = self.create_runbook(name='CUSTOM_RUNBOOK4', steps=steps)
        runbook.extra = {'answer': 42}

        runbook = self.operator_cloud.baremetal.update_runbook(runbook)
        self.assertEqual({'answer': 42}, runbook.extra)

        runbook = self.operator_cloud.baremetal.get_runbook(runbook.id)
        self.assertEqual({'answer': 42}, runbook.extra)

    def test_runbook_patch(self):
        name = "CUSTOM_HYPERTHREADING_ON"
        steps = [
            {
                "interface": "bios",
                "step": "apply_configuration",
                "args": {
                    "settings": [{"name": "LogicalProc", "value": "Enabled"}]
                },
                "order": 150,
            }
        ]
        runbook = self.create_runbook(name=name, steps=steps)
        runbook = self.operator_cloud.baremetal.patch_runbook(
            runbook, [{'path': '/extra/answer', 'op': 'add', 'value': 42}]
        )
        self.assertEqual({'answer': 42}, runbook.extra)
        self.assertEqual(name, runbook.name)

        runbook = self.operator_cloud.baremetal.get_runbook(runbook.id)
        self.assertEqual({'answer': 42}, runbook.extra)

    def test_runbook_negative_non_existing(self):
        uuid = "b4145fbb-d4bc-0d1d-4382-e1e922f9035c"
        self.assertRaises(
            exceptions.NotFoundException,
            self.operator_cloud.baremetal.get_runbook,
            uuid,
        )
        self.assertRaises(
            exceptions.NotFoundException,
            self.operator_cloud.baremetal.delete_runbook,
            uuid,
            ignore_missing=False,
        )
        self.assertIsNone(self.operator_cloud.baremetal.delete_runbook(uuid))

    def test_runbook_rbac_project_scoped(self):
        steps = [
            {
                "interface": "bios",
                "step": "apply_configuration",
                "args": {
                    "settings": [{"name": "LogicalProc", "value": "Enabled"}]
                },
                "order": 150,
            }
        ]

        runbook = self.operator_cloud.baremetal.create_runbook(
            name='CUSTOM_PROJ_AWESOME', steps=steps
        )
        self.addCleanup(
            lambda: self.operator_cloud.baremetal.delete_runbook(
                runbook.id, ignore_missing=True
            )
        )
        self.assertFalse(runbook.public)
        self.assertEqual(self.operator_cloud.current_project_id, runbook.owner)

        # is accessible to the owner
        loaded = self.operator_cloud.baremetal.get_runbook(runbook.id)
        self.assertEqual(loaded.id, runbook.id)

    def test_runbook_rbac_system_scoped(self):
        steps = [
            {
                "interface": "bios",
                "step": "apply_configuration",
                "args": {
                    "settings": [{"name": "LogicalProc", "value": "Enabled"}]
                },
                "order": 150,
            }
        ]

        runbook = self.system_admin_cloud.baremetal.create_runbook(
            name='CUSTOM_SYS_AWESOME', steps=steps
        )
        self.addCleanup(
            lambda: self.system_admin_cloud.baremetal.delete_runbook(
                runbook.id, ignore_missing=True
            )
        )

        self.assertFalse(runbook.public)
        self.assertIsNone(runbook.owner)

        # is accessible to system-scoped users
        loaded = self.system_admin_cloud.baremetal.get_runbook(runbook.id)
        self.assertEqual(loaded.id, runbook.id)


class TestBareMetalRunbookTraits(base.BaseBaremetalTest):
    min_microversion = '1.112'

    def setUp(self):
        super().setUp()
        self.steps = [
            {
                "interface": "bios",
                "step": "apply_configuration",
                "args": {
                    "settings": [{"name": "LogicalProc", "value": "Enabled"}]
                },
                "order": 150,
            }
        ]

    def test_runbook_description(self):
        runbook = self.create_runbook(
            name='CUSTOM_RUNBOOK_DESC',
            steps=self.steps,
            description='Enable logical processors',
        )
        self.assertEqual('Enable logical processors', runbook.description)

        runbook = self.operator_cloud.baremetal.patch_runbook(
            runbook,
            [{'path': '/description', 'op': 'replace', 'value': 'Updated'}],
        )
        self.assertEqual('Updated', runbook.description)

        runbook = self.operator_cloud.baremetal.get_runbook(runbook.id)
        self.assertEqual('Updated', runbook.description)

    def test_runbook_add_remove_trait(self):
        runbook = self.create_runbook(
            name='CUSTOM_RUNBOOK_TRAIT', steps=self.steps
        )
        self.assertEqual([], runbook.traits)

        self.operator_cloud.baremetal.add_runbook_trait(
            runbook, 'CUSTOM_TRAIT1'
        )
        runbook = self.operator_cloud.baremetal.get_runbook(runbook.id)
        self.assertEqual(['CUSTOM_TRAIT1'], runbook.traits)

        self.operator_cloud.baremetal.remove_runbook_trait(
            runbook, 'CUSTOM_TRAIT1'
        )
        runbook = self.operator_cloud.baremetal.get_runbook(runbook.id)
        self.assertEqual([], runbook.traits)

        # removing a trait that is not present is a no-op
        self.operator_cloud.baremetal.remove_runbook_trait(
            runbook, 'CUSTOM_TRAIT1'
        )

    def test_runbook_set_traits(self):
        runbook = self.create_runbook(
            name='CUSTOM_RUNBOOK_TRAITS', steps=self.steps
        )

        self.operator_cloud.baremetal.set_runbook_traits(
            runbook, ['CUSTOM_TRAIT1', 'CUSTOM_TRAIT2']
        )
        runbook = self.operator_cloud.baremetal.get_runbook(runbook.id)
        self.assertEqual(
            {'CUSTOM_TRAIT1', 'CUSTOM_TRAIT2'}, set(runbook.traits)
        )

        self.operator_cloud.baremetal.set_runbook_traits(runbook, [])
        runbook = self.operator_cloud.baremetal.get_runbook(runbook.id)
        self.assertEqual([], runbook.traits)

    def test_runbook_logical_name(self):
        # since 1.112 the name is no longer required to look like a trait
        runbook = self.create_runbook(
            name='enable-hyperthreading', steps=self.steps
        )
        self.assertEqual('enable-hyperthreading', runbook.name)

        loaded = self.operator_cloud.baremetal.get_runbook(
            'enable-hyperthreading'
        )
        self.assertEqual(runbook.id, loaded.id)
