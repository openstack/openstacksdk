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

"""
test_security_groups
----------------------------------

Functional tests for security_groups resource.
"""

from openstack.tests.functional import base


class TestSecurityGroups(base.BaseFunctionalTest):
    def test_create_list_security_groups(self):
        sg1 = self.user_cloud.create_security_group(
            name="sg1", description="sg1"
        )
        self.addCleanup(self.user_cloud.delete_security_group, sg1['id'])
        if self.user_cloud.has_service('network'):
            # Neutron defaults to all_tenants=1 when admin
            sg_list = self.user_cloud.list_security_groups()
            self.assertIn(sg1['id'], [sg['id'] for sg in sg_list])

        else:
            # Nova does not list all tenants by default
            sg_list = self.operator_cloud.list_security_groups()

    def test_create_list_security_groups_operator(self):
        if not self.operator_cloud:
            self.skipTest("Operator cloud is required for this test")

        sg1 = self.user_cloud.create_security_group(
            name="sg1", description="sg1"
        )
        self.addCleanup(self.user_cloud.delete_security_group, sg1['id'])
        sg2 = self.operator_cloud.create_security_group(
            name="sg2", description="sg2"
        )
        self.addCleanup(self.operator_cloud.delete_security_group, sg2['id'])

        if self.user_cloud.has_service('network'):
            # Neutron defaults to all_tenants=1 when admin
            sg_list = self.operator_cloud.list_security_groups()
            self.assertIn(sg1['id'], [sg['id'] for sg in sg_list])

            # Filter by tenant_id (filtering by project_id won't work with
            # Keystone V2)
            sg_list = self.operator_cloud.list_security_groups(
                filters={'tenant_id': self.user_cloud.current_project_id}
            )
            self.assertIn(sg1['id'], [sg['id'] for sg in sg_list])
            self.assertNotIn(sg2['id'], [sg['id'] for sg in sg_list])

        else:
            # Nova does not list all tenants by default
            sg_list = self.operator_cloud.list_security_groups()
            self.assertIn(sg2['id'], [sg['id'] for sg in sg_list])
            self.assertNotIn(sg1['id'], [sg['id'] for sg in sg_list])

            sg_list = self.operator_cloud.list_security_groups(
                filters={'all_tenants': 1}
            )
            self.assertIn(sg1['id'], [sg['id'] for sg in sg_list])

    def test_get_security_group_by_id(self):
        sg = self.user_cloud.create_security_group(name='sg', description='sg')
        self.addCleanup(self.user_cloud.delete_security_group, sg['id'])

        ret_sg = self.user_cloud.get_security_group_by_id(sg['id'])
        self.assertEqual(sg, ret_sg)
