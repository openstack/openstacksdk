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

from shade import exc
from shade.tests.unit import base

fake_quota_set = {
    "cores": 20,
    "fixed_ips": -1,
    "floating_ips": 10,
    "injected_file_content_bytes": 10240,
    "injected_file_path_bytes": 255,
    "injected_files": 5,
    "instances": 10,
    "key_pairs": 100,
    "metadata_items": 128,
    "ram": 51200,
    "security_group_rules": 20,
    "security_groups": 45,
    "server_groups": 10,
    "server_group_members": 10
}


class TestQuotas(base.RequestsMockTestCase):
    def setUp(self, cloud_config_fixture='clouds.yaml'):
        super(TestQuotas, self).setUp(
            cloud_config_fixture=cloud_config_fixture)

    def test_update_quotas(self):
        project = self.mock_for_keystone_projects(project_count=1,
                                                  list_get=True)[0]

        self.register_uris([
            dict(method='PUT',
                 uri=self.get_mock_url(
                     'compute', 'public',
                     append=['os-quota-sets', project.project_id]),
                 json={'quota_set': fake_quota_set},
                 validate=dict(
                     json={
                         'quota_set': {
                             'cores': 1,
                             'force': True
                         }})),
        ])

        self.op_cloud.set_compute_quotas(project.project_id, cores=1)

        self.assert_calls()

    def test_update_quotas_bad_request(self):
        project = self.mock_for_keystone_projects(project_count=1,
                                                  list_get=True)[0]

        self.register_uris([
            dict(method='PUT',
                 uri=self.get_mock_url(
                     'compute', 'public',
                     append=['os-quota-sets', project.project_id]),
                 status_code=400),
        ])

        self.assertRaises(exc.OpenStackCloudException,
                          self.op_cloud.set_compute_quotas, project.project_id)

        self.assert_calls()

    def test_get_quotas(self):
        project = self.mock_for_keystone_projects(project_count=1,
                                                  list_get=True)[0]
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public',
                     append=['os-quota-sets', project.project_id]),
                 json={'quota_set': fake_quota_set}),
        ])

        self.op_cloud.get_compute_quotas(project.project_id)

        self.assert_calls()

    def test_delete_quotas(self):
        project = self.mock_for_keystone_projects(project_count=1,
                                                  list_get=True)[0]

        self.register_uris([
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'compute', 'public',
                     append=['os-quota-sets', project.project_id])),
        ])

        self.op_cloud.delete_compute_quotas(project.project_id)

        self.assert_calls()

    def test_cinder_update_quotas(self):
        project = self.mock_for_keystone_projects(project_count=1,
                                                  list_get=True)[0]
        self.register_uris([
            dict(method='PUT',
                 uri=self.get_mock_url(
                     'volumev2', 'public',
                     append=['os-quota-sets', project.project_id]),
                 json=dict(quota_set={'volumes': 1}),
                 validate=dict(
                     json={'quota_set': {
                         'volumes': 1,
                         'tenant_id': project.project_id}}))])
        self.op_cloud.set_volume_quotas(project.project_id, volumes=1)
        self.assert_calls()

    def test_cinder_get_quotas(self):
        project = self.mock_for_keystone_projects(project_count=1,
                                                  list_get=True)[0]
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'volumev2', 'public',
                     append=['os-quota-sets', project.project_id]),
                 json=dict(quota_set={'snapshots': 10, 'volumes': 20}))])
        self.op_cloud.get_volume_quotas(project.project_id)
        self.assert_calls()

    def test_cinder_delete_quotas(self):
        project = self.mock_for_keystone_projects(project_count=1,
                                                  list_get=True)[0]
        self.register_uris([
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'volumev2', 'public',
                     append=['os-quota-sets', project.project_id]))])
        self.op_cloud.delete_volume_quotas(project.project_id)
        self.assert_calls()

    def test_neutron_update_quotas(self):
        project = self.mock_for_keystone_projects(project_count=1,
                                                  list_get=True)[0]
        self.register_uris([
            dict(method='PUT',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'quotas',
                             '%s.json' % project.project_id]),
                 json={},
                 validate=dict(
                     json={'quota': {'network': 1}}))
        ])
        self.op_cloud.set_network_quotas(project.project_id, network=1)
        self.assert_calls()

    def test_neutron_get_quotas(self):
        quota = {
            'subnet': 100,
            'network': 100,
            'floatingip': 50,
            'subnetpool': -1,
            'security_group_rule': 100,
            'security_group': 10,
            'router': 10,
            'rbac_policy': 10,
            'port': 500
        }
        project = self.mock_for_keystone_projects(project_count=1,
                                                  list_get=True)[0]
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'quotas',
                             '%s.json' % project.project_id]),
                 json={'quota': quota})
        ])
        received_quota = self.op_cloud.get_network_quotas(project.project_id)
        self.assertDictEqual(quota, received_quota)
        self.assert_calls()

    def test_neutron_delete_quotas(self):
        project = self.mock_for_keystone_projects(project_count=1,
                                                  list_get=True)[0]
        self.register_uris([
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'quotas',
                             '%s.json' % project.project_id]),
                 json={})
        ])
        self.op_cloud.delete_network_quotas(project.project_id)
        self.assert_calls()
