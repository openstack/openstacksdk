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

import shade
from shade.tests import fakes
from shade.tests.unit import base


class TestFlavors(base.TestCase):

    def setUp(self):
        super(TestFlavors, self).setUp()
        self.op_cloud = shade.operator_cloud(validate=False)

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_create_flavor(self, mock_nova):
        self.op_cloud.create_flavor(
            'vanilla', 12345, 4, 100
        )
        mock_nova.flavors.create.assert_called_once_with(
            name='vanilla', ram=12345, vcpus=4, disk=100,
            flavorid='auto', ephemeral=0, swap=0, rxtx_factor=1.0,
            is_public=True
        )

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_delete_flavor(self, mock_nova):
        mock_nova.flavors.list.return_value = [
            fakes.FakeFlavor('123', 'lemon')
        ]
        self.assertTrue(self.op_cloud.delete_flavor('lemon'))
        mock_nova.flavors.delete.assert_called_once_with(flavor='123')

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_delete_flavor_not_found(self, mock_nova):
        mock_nova.flavors.list.return_value = []
        self.assertFalse(self.op_cloud.delete_flavor('invalid'))
        self.assertFalse(mock_nova.flavors.delete.called)

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_delete_flavor_exception(self, mock_nova):
        mock_nova.flavors.list.return_value = [
            fakes.FakeFlavor('123', 'lemon')
        ]
        mock_nova.flavors.delete.side_effect = Exception()
        self.assertRaises(shade.OpenStackCloudException,
                          self.op_cloud.delete_flavor, '')

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_list_flavors(self, mock_nova):
        self.op_cloud.list_flavors()
        mock_nova.flavors.list.assert_called_once_with(is_public=None)

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_set_flavor_specs(self, mock_nova):
        flavor = mock.Mock(id=1, name='orange')
        mock_nova.flavors.get.return_value = flavor
        extra_specs = dict(key1='value1')
        self.op_cloud.set_flavor_specs(1, extra_specs)
        mock_nova.flavors.get.assert_called_once_with(flavor=1)
        flavor.set_keys.assert_called_once_with(extra_specs)

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_unset_flavor_specs(self, mock_nova):
        flavor = mock.Mock(id=1, name='orange')
        mock_nova.flavors.get.return_value = flavor
        keys = ['key1', 'key2']
        self.op_cloud.unset_flavor_specs(1, keys)
        mock_nova.flavors.get.assert_called_once_with(flavor=1)
        flavor.unset_keys.assert_called_once_with(keys)

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_add_flavor_access(self, mock_nova):
        self.op_cloud.add_flavor_access('flavor_id', 'tenant_id')
        mock_nova.flavor_access.add_tenant_access.assert_called_once_with(
            flavor='flavor_id', tenant='tenant_id'
        )

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_remove_flavor_access(self, mock_nova):
        self.op_cloud.remove_flavor_access('flavor_id', 'tenant_id')
        mock_nova.flavor_access.remove_tenant_access.assert_called_once_with(
            flavor='flavor_id', tenant='tenant_id'
        )
