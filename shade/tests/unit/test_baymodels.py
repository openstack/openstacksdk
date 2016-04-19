# -*- coding: utf-8 -*-

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


baymodel_obj = munch.Munch(
    apiserver_port=None,
    uuid='fake-uuid',
    human_id=None,
    name='fake-baymodel',
    server_type='vm',
    public=False,
    image_id='fake-image',
    tls_disabled=False,
    registry_enabled=False,
    coe='fake-coe',
    keypair_id='fake-key',
)

baymodel_detail_obj = munch.Munch(
    links={},
    labels={},
    apiserver_port=None,
    uuid='fake-uuid',
    human_id=None,
    name='fake-baymodel',
    server_type='vm',
    public=False,
    image_id='fake-image',
    tls_disabled=False,
    registry_enabled=False,
    coe='fake-coe',
    created_at='fake-date',
    updated_at=None,
    master_flavor_id=None,
    no_proxy=None,
    https_proxy=None,
    keypair_id='fake-key',
    docker_volume_size=1,
    external_network_id='public',
    cluster_distro='fake-distro',
    volume_driver=None,
    network_driver='fake-driver',
    fixed_network=None,
    flavor_id='fake-flavor',
    dns_nameserver='8.8.8.8',
)


class TestBaymodels(base.TestCase):

    def setUp(self):
        super(TestBaymodels, self).setUp()
        self.cloud = shade.openstack_cloud(validate=False)

    @mock.patch.object(shade.OpenStackCloud, 'magnum_client')
    def test_list_baymodels_without_detail(self, mock_magnum):
        mock_magnum.baymodels.list.return_value = [baymodel_obj, ]
        baymodels_list = self.cloud.list_baymodels()
        mock_magnum.baymodels.list.assert_called_with(detail=False)
        self.assertEqual(baymodels_list[0], baymodel_obj)

    @mock.patch.object(shade.OpenStackCloud, 'magnum_client')
    def test_list_baymodels_with_detail(self, mock_magnum):
        mock_magnum.baymodels.list.return_value = [baymodel_detail_obj, ]
        baymodels_list = self.cloud.list_baymodels(detail=True)
        mock_magnum.baymodels.list.assert_called_with(detail=True)
        self.assertEqual(baymodels_list[0], baymodel_detail_obj)

    @mock.patch.object(shade.OpenStackCloud, 'magnum_client')
    def test_search_baymodels_by_name(self, mock_magnum):
        mock_magnum.baymodels.list.return_value = [baymodel_obj, ]

        baymodels = self.cloud.search_baymodels(name_or_id='fake-baymodel')
        mock_magnum.baymodels.list.assert_called_with(detail=False)

        self.assertEquals(1, len(baymodels))
        self.assertEquals('fake-uuid', baymodels[0]['uuid'])

    @mock.patch.object(shade.OpenStackCloud, 'magnum_client')
    def test_search_baymodels_not_found(self, mock_magnum):
        mock_magnum.baymodels.list.return_value = [baymodel_obj, ]

        baymodels = self.cloud.search_baymodels(name_or_id='non-existent')

        mock_magnum.baymodels.list.assert_called_with(detail=False)
        self.assertEquals(0, len(baymodels))

    @mock.patch.object(shade.OpenStackCloud, 'search_baymodels')
    def test_get_baymodel(self, mock_search):
        mock_search.return_value = [baymodel_obj, ]
        r = self.cloud.get_baymodel('fake-baymodel')
        self.assertIsNotNone(r)
        self.assertDictEqual(baymodel_obj, r)

    @mock.patch.object(shade.OpenStackCloud, 'search_baymodels')
    def test_get_baymodel_not_found(self, mock_search):
        mock_search.return_value = []
        r = self.cloud.get_baymodel('doesNotExist')
        self.assertIsNone(r)

    @mock.patch.object(shade.OpenStackCloud, 'magnum_client')
    def test_create_baymodel(self, mock_magnum):
        self.cloud.create_baymodel(
            name=baymodel_obj.name, image_id=baymodel_obj.image_id,
            keypair_id=baymodel_obj.keypair_id, coe=baymodel_obj.coe)
        mock_magnum.baymodels.create.assert_called_once_with(
            name=baymodel_obj.name, image_id=baymodel_obj.image_id,
            keypair_id=baymodel_obj.keypair_id, coe=baymodel_obj.coe
        )

    @mock.patch.object(shade.OpenStackCloud, 'magnum_client')
    def test_create_baymodel_exception(self, mock_magnum):
        mock_magnum.baymodels.create.side_effect = Exception()
        with testtools.ExpectedException(
            shade.OpenStackCloudException,
            "Error creating baymodel of name fake-baymodel"
        ):
            self.cloud.create_baymodel('fake-baymodel')

    @mock.patch.object(shade.OpenStackCloud, 'magnum_client')
    def test_delete_baymodel(self, mock_magnum):
        mock_magnum.baymodels.list.return_value = [baymodel_obj]
        self.cloud.delete_baymodel('fake-uuid')
        mock_magnum.baymodels.delete.assert_called_once_with(
            'fake-uuid'
        )

    @mock.patch.object(shade.OpenStackCloud, 'magnum_client')
    def test_update_baymodel(self, mock_magnum):
        new_name = 'new-baymodel'
        mock_magnum.baymodels.list.return_value = [baymodel_obj]
        self.cloud.update_baymodel('fake-uuid', 'replace', name=new_name)
        mock_magnum.baymodels.update.assert_called_once_with(
            'fake-uuid', [{'path': '/name', 'op': 'replace',
                           'value': 'new-baymodel'}]
        )
