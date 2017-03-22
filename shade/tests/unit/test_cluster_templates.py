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
import munch

import shade
import testtools
from shade.tests.unit import base


cluster_template_obj = munch.Munch(
    apiserver_port=12345,
    cluster_distro='fake-distro',
    coe='fake-coe',
    created_at='fake-date',
    dns_nameserver='8.8.8.8',
    docker_volume_size=1,
    external_network_id='public',
    fixed_network=None,
    flavor_id='fake-flavor',
    https_proxy=None,
    human_id=None,
    image_id='fake-image',
    insecure_registry='https://192.168.0.10',
    keypair_id='fake-key',
    labels={},
    links={},
    master_flavor_id=None,
    name='fake-cluster-template',
    network_driver='fake-driver',
    no_proxy=None,
    public=False,
    registry_enabled=False,
    server_type='vm',
    tls_disabled=False,
    updated_at=None,
    uuid='fake-uuid',
    volume_driver=None,
)


class TestClusterTemplates(base.RequestsMockTestCase):

    def test_list_cluster_templates_without_detail(self):

        self.register_uris([dict(
            method='GET',
            uri='https://container-infra.example.com/v1/baymodels/detail',
            json=dict(baymodels=[cluster_template_obj.toDict()]))])
        cluster_templates_list = self.cloud.list_cluster_templates()
        self.assertEqual(
            cluster_templates_list[0],
            self.cloud._normalize_cluster_template(cluster_template_obj))
        self.assert_calls()

    def test_list_cluster_templates_with_detail(self):
        self.register_uris([dict(
            method='GET',
            uri='https://container-infra.example.com/v1/baymodels/detail',
            json=dict(baymodels=[cluster_template_obj.toDict()]))])
        cluster_templates_list = self.cloud.list_cluster_templates(detail=True)
        self.assertEqual(
            cluster_templates_list[0],
            self.cloud._normalize_cluster_template(
                cluster_template_obj))
        self.assert_calls()

    @mock.patch.object(shade.OpenStackCloud, 'magnum_client')
    def test_search_cluster_templates_by_name(self, mock_magnum):
        mock_magnum.baymodels.list.return_value = [
            cluster_template_obj]

        cluster_templates = self.cloud.search_cluster_templates(
            name_or_id='fake-cluster-template')
        mock_magnum.baymodels.list.assert_called_with(detail=True)

        self.assertEqual(1, len(cluster_templates))
        self.assertEqual('fake-uuid', cluster_templates[0]['uuid'])

    @mock.patch.object(shade.OpenStackCloud, 'magnum_client')
    def test_search_cluster_templates_not_found(self, mock_magnum):
        mock_magnum.baymodels.list.return_value = [
            cluster_template_obj]

        cluster_templates = self.cloud.search_cluster_templates(
            name_or_id='non-existent')

        mock_magnum.baymodels.list.assert_called_with(detail=True)
        self.assertEqual(0, len(cluster_templates))

    @mock.patch.object(shade.OpenStackCloud, 'search_cluster_templates')
    def test_get_cluster_template(self, mock_search):
        mock_search.return_value = [cluster_template_obj, ]
        r = self.cloud.get_cluster_template('fake-cluster-template')
        self.assertIsNotNone(r)
        self.assertDictEqual(cluster_template_obj, r)

    @mock.patch.object(shade.OpenStackCloud, 'search_cluster_templates')
    def test_get_cluster_template_not_found(self, mock_search):
        mock_search.return_value = []
        r = self.cloud.get_cluster_template('doesNotExist')
        self.assertIsNone(r)

    @mock.patch.object(shade.OpenStackCloud, 'magnum_client')
    def test_create_cluster_template(self, mock_magnum):
        self.cloud.create_cluster_template(
            name=cluster_template_obj.name,
            image_id=cluster_template_obj.image_id,
            keypair_id=cluster_template_obj.keypair_id,
            coe=cluster_template_obj.coe)
        mock_magnum.baymodels.create.assert_called_once_with(
            name=cluster_template_obj.name,
            image_id=cluster_template_obj.image_id,
            keypair_id=cluster_template_obj.keypair_id,
            coe=cluster_template_obj.coe
        )

    @mock.patch.object(shade.OpenStackCloud, 'magnum_client')
    def test_create_cluster_template_exception(self, mock_magnum):
        mock_magnum.baymodels.create.side_effect = Exception()
        with testtools.ExpectedException(
            shade.OpenStackCloudException,
            "Error creating cluster template of name fake-cluster-template"
        ):
            self.cloud.create_cluster_template('fake-cluster-template')

    @mock.patch.object(shade.OpenStackCloud, 'magnum_client')
    def test_delete_cluster_template(self, mock_magnum):
        mock_magnum.baymodels.list.return_value = [
            cluster_template_obj]
        self.cloud.delete_cluster_template('fake-uuid')
        mock_magnum.baymodels.delete.assert_called_once_with(
            'fake-uuid'
        )

    @mock.patch.object(shade.OpenStackCloud, 'magnum_client')
    def test_update_cluster_template(self, mock_magnum):
        new_name = 'new-cluster-template'
        mock_magnum.baymodels.list.return_value = [
            cluster_template_obj]
        self.cloud.update_cluster_template(
            'fake-uuid', 'replace', name=new_name)
        mock_magnum.baymodels.update.assert_called_once_with(
            'fake-uuid', [{'path': '/name', 'op': 'replace',
                           'value': 'new-cluster-template'}]
        )
