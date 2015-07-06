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
        self.op_cloud = shade.operator_cloud()

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
