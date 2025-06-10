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


class TestBareMetalRunbook(base.BaseBaremetalTest):
    min_microversion = '1.92'

    def setUp(self):
        super().setUp()

    def test_baremetal_runbook_create_get_delete(self):
        steps = [
            {
                "interface": "bios",
                "step": "apply_configuration",
                "args": {
                    "settings": [{"name": "LogicalProc", "value": "Enabled"}]
                },
                "priority": 150,
            }
        ]
        runbook = self.create_runbook(name='CUSTOM_RUNBOOK', steps=steps)
        loaded = self.conn.baremetal.get_runbook(runbook.id)
        self.assertEqual(loaded.id, runbook.id)
        self.conn.baremetal.delete_runbook(runbook, ignore_missing=False)
        self.assertRaises(
            exceptions.NotFoundException,
            self.conn.baremetal.get_runbook,
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
                "priority": 150,
            }
        ]

        runbook1 = self.create_runbook(name='CUSTOM_RUNBOOK1', steps=steps)
        runbook2 = self.create_runbook(name='CUSTOM_RUNBOOK2', steps=steps)
        runbooks = self.conn.baremetal.runbooks()
        ids = [runbook.id for runbook in runbooks]
        self.assertIn(runbook1.id, ids)
        self.assertIn(runbook2.id, ids)

        runbooks_with_details = self.conn.baremetal.runbooks(details=True)
        for runbook in runbooks_with_details:
            self.assertIsNotNone(runbook.id)
            self.assertIsNotNone(runbook.name)

        runbook_with_fields = self.conn.baremetal.runbooks(fields=['uuid'])
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
                "priority": 150,
            }
        ]
        runbook = self.create_runbook(name='CUSTOM_RUNBOOK4', steps=steps)
        self.assertFalse(runbook.extra)
        runbook.extra = {'answer': 42}

        runbook = self.conn.baremetal.update_runbook(runbook)
        self.assertEqual({'answer': 42}, runbook.extra)

        runbook = self.conn.baremetal.get_runbook(runbook.id)

        self.conn.baremetal.delete_runbook(runbook.id, ignore_missing=False)

    def test_baremetal_runbook_update(self):
        steps = [
            {
                "interface": "bios",
                "step": "apply_configuration",
                "args": {
                    "settings": [{"name": "LogicalProc", "value": "Enabled"}]
                },
                "priority": 150,
            }
        ]
        runbook = self.create_runbook(name='CUSTOM_RUNBOOK4', steps=steps)
        runbook.extra = {'answer': 42}

        runbook = self.conn.baremetal.update_runbook(runbook)
        self.assertEqual({'answer': 42}, runbook.extra)

        runbook = self.conn.baremetal.get_runbook(runbook.id)
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
                "priority": 150,
            }
        ]
        runbook = self.create_runbook(name=name, steps=steps)
        runbook = self.conn.baremetal.patch_runbook(
            runbook, dict(path='/extra/answer', op='add', value=42)
        )
        self.assertEqual({'answer': 42}, runbook.extra)
        self.assertEqual(name, runbook.name)

        runbook = self.conn.baremetal.get_runbook(runbook.id)
        self.assertEqual({'answer': 42}, runbook.extra)

    def test_runbook_negative_non_existing(self):
        uuid = "b4145fbb-d4bc-0d1d-4382-e1e922f9035c"
        self.assertRaises(
            exceptions.NotFoundException,
            self.conn.baremetal.get_runbook,
            uuid,
        )
        self.assertRaises(
            exceptions.NotFoundException,
            self.conn.baremetal.delete_runbook,
            uuid,
            ignore_missing=False,
        )
        self.assertIsNone(self.conn.baremetal.delete_runbook(uuid))

    def test_runbook_rbac_project_scoped(self):
        steps = [
            {
                "interface": "bios",
                "step": "apply_configuration",
                "args": {
                    "settings": [{"name": "LogicalProc", "value": "Enabled"}]
                },
                "priority": 150,
            }
        ]

        runbook = self.create_runbook(
            name='CUSTOM_PROJ_AWESOME',
            steps=steps,
            owner=self.conn.current_project_id,
        )
        self.assertFalse(runbook.public)
        self.assertEqual(self.conn.current_project_id, runbook.owner)

        # is accessible to the owner
        loaded = self.conn.baremetal.get_runbook(runbook.id)
        self.assertEqual(loaded.id, runbook.id)

    def test_runbook_rbac_system_scoped(self):
        steps = [
            {
                "interface": "bios",
                "step": "apply_configuration",
                "args": {
                    "settings": [{"name": "LogicalProc", "value": "Enabled"}]
                },
                "priority": 150,
            }
        ]

        runbook = self.create_runbook(name='CUSTOM_SYS_AWESOME', steps=steps)
        self.assertFalse(runbook.public)
        self.assertIsNone(runbook.owner)

        # is accessible to system-scoped users
        loaded = self.conn.baremetal.get_runbook(runbook.id)
        self.assertEqual(loaded.id, runbook.id)
