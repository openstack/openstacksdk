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


import mock
from novaclient import exceptions as nova_exceptions

import shade
from shade import exc
from shade.tests.unit import base


class TestQuotas(base.RequestsMockTestCase):
    def setUp(self, cloud_config_fixture='clouds.yaml'):
        super(TestQuotas, self).setUp(
            cloud_config_fixture=cloud_config_fixture)
        self._add_discovery_uri_call()

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_update_quotas(self, mock_nova):
        project = self.mock_for_keystone_projects(project_count=1,
                                                  list_get=True)[0]
        # re-mock the list-get as the call to set_compute_quotas when
        # bad-request is raised, still calls out to get the project data.
        self.mock_for_keystone_projects(project=project, list_get=True)

        self.op_cloud.set_compute_quotas(project.project_id, cores=1)

        mock_nova.quotas.update.assert_called_once_with(
            cores=1, force=True, tenant_id=project.project_id)

        mock_nova.quotas.update.side_effect = nova_exceptions.BadRequest(400)
        self.assertRaises(exc.OpenStackCloudException,
                          self.op_cloud.set_compute_quotas, project)
        self.assert_calls()

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_get_quotas(self, mock_nova):
        project = self.mock_for_keystone_projects(project_count=1,
                                                  list_get=True)[0]
        self.op_cloud.get_compute_quotas(project.project_id)

        mock_nova.quotas.get.assert_called_once_with(
            tenant_id=project.project_id)

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_delete_quotas(self, mock_nova):
        project = self.mock_for_keystone_projects(project_count=1,
                                                  list_get=True)[0]
        # re-mock the list-get as the call to set_delete_compute_quotas when
        # bad-request is raised, still calls out to get the project data.
        self.mock_for_keystone_projects(project=project, list_get=True)

        self.op_cloud.delete_compute_quotas(project.project_id)

        mock_nova.quotas.delete.assert_called_once_with(
            tenant_id=project.project_id)

        mock_nova.quotas.delete.side_effect = nova_exceptions.BadRequest(400)
        self.assertRaises(exc.OpenStackCloudException,
                          self.op_cloud.delete_compute_quotas, project)
        self.assert_calls()

    @mock.patch.object(shade.OpenStackCloud, 'cinder_client')
    def test_cinder_update_quotas(self, mock_cinder):
        project = self.mock_for_keystone_projects(project_count=1,
                                                  list_get=True)[0]
        self.op_cloud.set_volume_quotas(project.project_id, volumes=1)

        mock_cinder.quotas.update.assert_called_once_with(
            volumes=1, tenant_id=project.project_id)
        self.assert_calls()

    @mock.patch.object(shade.OpenStackCloud, 'cinder_client')
    def test_cinder_get_quotas(self, mock_cinder):
        project = self.mock_for_keystone_projects(project_count=1,
                                                  list_get=True)[0]
        self.op_cloud.get_volume_quotas(project.project_id)

        mock_cinder.quotas.get.assert_called_once_with(
            tenant_id=project.project_id)
        self.assert_calls()

    @mock.patch.object(shade.OpenStackCloud, 'cinder_client')
    def test_cinder_delete_quotas(self, mock_cinder):
        project = self.mock_for_keystone_projects(project_count=1,
                                                  list_get=True)[0]
        self.op_cloud.delete_volume_quotas(project.project_id)

        mock_cinder.quotas.delete.assert_called_once_with(
            tenant_id=project.project_id)
        self.assert_calls()

    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_neutron_update_quotas(self, mock_neutron):
        project = self.mock_for_keystone_projects(project_count=1,
                                                  list_get=True)[0]
        self.op_cloud.set_network_quotas(project.project_id, network=1)

        mock_neutron.update_quota.assert_called_once_with(
            body={'quota': {'network': 1}}, tenant_id=project.project_id)
        self.assert_calls()

    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_neutron_get_quotas(self, mock_neutron):
        project = self.mock_for_keystone_projects(project_count=1,
                                                  list_get=True)[0]
        self.op_cloud.get_network_quotas(project.project_id)

        mock_neutron.show_quota.assert_called_once_with(
            tenant_id=project.project_id)
        self.assert_calls()

    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_neutron_delete_quotas(self, mock_neutron):
        project = self.mock_for_keystone_projects(project_count=1,
                                                  list_get=True)[0]
        self.op_cloud.delete_network_quotas(project.project_id)

        mock_neutron.delete_quota.assert_called_once_with(
            tenant_id=project.project_id)
        self.assert_calls()
