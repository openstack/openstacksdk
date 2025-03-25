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

from openstack.tests.functional import base


class TestAutoAllocatedTopology(base.BaseFunctionalTest):
    NETWORK_NAME = "auto_allocated_network"
    NETWORK_ID = None
    PROJECT_ID = None

    def setUp(self):
        super().setUp()

        if not self.operator_cloud:
            self.skipTest("Operator cloud is required for this test")

        if not self.operator_cloud._has_neutron_extension(
            "auto-allocated-topology"
        ):
            self.skipTest(
                "Neutron auto-allocated-topology extension is "
                "required for this test"
            )

        project = self._create_project()
        self.PROJECT_ID = project['id']
        self.test_cloud = self.operator_cloud.connect_as_project(project)

        # Dry run will only pass if there is a public network
        self._set_network_external()

    def tearDown(self):
        res = self.test_cloud.network.delete_auto_allocated_topology(
            self.PROJECT_ID
        )
        self.assertIsNone(res)
        self._destroy_project()
        super().tearDown()

    def _create_project(self):
        project_name = 'auto_allocated_topology_test_project'
        project = self.operator_cloud.get_project(project_name)
        if not project:
            params = {
                'name': project_name,
                'description': (
                    'test project used only for the '
                    'TestAutoAllocatedTopology tests class'
                ),
                'domain_id': self.operator_cloud.get_domain('default')['id'],
            }

            project = self.operator_cloud.create_project(**params)

        user_id = self.operator_cloud.current_user_id
        # Grant the current user access to the project
        role_assignment = self.operator_cloud.list_role_assignments(
            {'user': user_id, 'project': project['id']}
        )
        if not role_assignment:
            self.operator_cloud.grant_role(
                'member', user=user_id, project=project['id'], wait=True
            )
        return project

    def _destroy_project(self):
        self.operator_cloud.revoke_role(
            'member',
            user=self.operator_cloud.current_user_id,
            project=self.PROJECT_ID,
        )
        self.operator_cloud.delete_project(self.PROJECT_ID)

    def test_auto_allocated_topology(self):
        # First test validation with the 'dry-run' call
        # Dry run option will return "dry-run=pass" in the 'id' resource
        top = self.test_cloud.network.validate_auto_allocated_topology(
            self.PROJECT_ID
        )
        self.assertEqual(self.PROJECT_ID, top.project)
        self.assertEqual("dry-run=pass", top.id)

        # test show auto_allocated_network without project id in the request
        top = self.test_cloud.network.get_auto_allocated_topology()
        project = self.test_cloud.session.get_project_id()
        network = self.test_cloud.network.get_network(top.id)
        self.assertEqual(top.project_id, project)
        self.assertEqual(top.id, network.id)

        # test show auto_allocated_network with project id in the request
        top = self.test_cloud.network.get_auto_allocated_topology(
            self.PROJECT_ID
        )
        network = self.test_cloud.network.get_network(top.id)
        self.assertEqual(top.project_id, network.project_id)
        self.assertEqual(top.id, network.id)
        self.assertEqual(network.name, "auto_allocated_network")

    def _set_network_external(self):
        networks = self.test_cloud.network.networks()
        for network in networks:
            if network.name == "public":
                self.test_cloud.network.update_network(
                    network, is_default=True
                )
