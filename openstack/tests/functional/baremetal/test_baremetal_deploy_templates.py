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


class TestBareMetalDeployTemplate(base.BaseBaremetalTest):
    min_microversion = '1.55'

    def setUp(self):
        super().setUp()

    def test_baremetal_deploy_create_get_delete(self):
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
        deploy_template = self.create_deploy_template(
            name='CUSTOM_DEPLOY_TEMPLATE', steps=steps
        )
        loaded = self.operator_cloud.baremetal.get_deploy_template(
            deploy_template.id
        )
        self.assertEqual(loaded.id, deploy_template.id)
        self.operator_cloud.baremetal.delete_deploy_template(
            deploy_template, ignore_missing=False
        )
        self.assertRaises(
            exceptions.NotFoundException,
            self.operator_cloud.baremetal.get_deploy_template,
            deploy_template.id,
        )

    def test_baremetal_deploy_template_list(self):
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

        deploy_template1 = self.create_deploy_template(
            name='CUSTOM_DEPLOY_TEMPLATE1', steps=steps
        )
        deploy_template2 = self.create_deploy_template(
            name='CUSTOM_DEPLOY_TEMPLATE2', steps=steps
        )
        deploy_templates = self.operator_cloud.baremetal.deploy_templates()
        ids = [template.id for template in deploy_templates]
        self.assertIn(deploy_template1.id, ids)
        self.assertIn(deploy_template2.id, ids)

        deploy_templates_with_details = (
            self.operator_cloud.baremetal.deploy_templates(details=True)
        )
        for dp in deploy_templates_with_details:
            self.assertIsNotNone(dp.id)
            self.assertIsNotNone(dp.name)

        deploy_tempalte_with_fields = (
            self.operator_cloud.baremetal.deploy_templates(fields=['uuid'])
        )
        for dp in deploy_tempalte_with_fields:
            self.assertIsNotNone(dp.id)
            self.assertIsNone(dp.name)

    def test_baremetal_deploy_list_update_delete(self):
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
        deploy_template = self.create_deploy_template(
            name='CUSTOM_DEPLOY_TEMPLATE4', steps=steps
        )
        self.assertFalse(deploy_template.extra)
        deploy_template.extra = {'answer': 42}

        deploy_template = self.operator_cloud.baremetal.update_deploy_template(
            deploy_template
        )
        self.assertEqual({'answer': 42}, deploy_template.extra)

        deploy_template = self.operator_cloud.baremetal.get_deploy_template(
            deploy_template.id
        )

        self.operator_cloud.baremetal.delete_deploy_template(
            deploy_template.id, ignore_missing=False
        )

    def test_baremetal_deploy_update(self):
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
        deploy_template = self.create_deploy_template(
            name='CUSTOM_DEPLOY_TEMPLATE4', steps=steps
        )
        deploy_template.extra = {'answer': 42}

        deploy_template = self.operator_cloud.baremetal.update_deploy_template(
            deploy_template
        )
        self.assertEqual({'answer': 42}, deploy_template.extra)

        deploy_template = self.operator_cloud.baremetal.get_deploy_template(
            deploy_template.id
        )
        self.assertEqual({'answer': 42}, deploy_template.extra)

    def test_deploy_template_patch(self):
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
        deploy_template = self.create_deploy_template(name=name, steps=steps)
        deploy_template = self.operator_cloud.baremetal.patch_deploy_template(
            deploy_template, dict(path='/extra/answer', op='add', value=42)
        )
        self.assertEqual({'answer': 42}, deploy_template.extra)
        self.assertEqual(name, deploy_template.name)

        deploy_template = self.operator_cloud.baremetal.get_deploy_template(
            deploy_template.id
        )
        self.assertEqual({'answer': 42}, deploy_template.extra)

    def test_deploy_template_negative_non_existing(self):
        uuid = "bbb45f41-d4bc-4307-8d1d-32f95ce1e920"
        self.assertRaises(
            exceptions.NotFoundException,
            self.operator_cloud.baremetal.get_deploy_template,
            uuid,
        )
        self.assertRaises(
            exceptions.NotFoundException,
            self.operator_cloud.baremetal.delete_deploy_template,
            uuid,
            ignore_missing=False,
        )
        self.assertIsNone(
            self.operator_cloud.baremetal.delete_deploy_template(uuid)
        )
