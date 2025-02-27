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

from openstack.compute.v2 import server
from openstack.tests.functional.compute import base as ft_base
from openstack.tests.functional.network.v2 import test_network


class TestServerAdmin(ft_base.BaseComputeTest):
    def setUp(self):
        super().setUp()
        self.NAME = 'needstobeshortandlowercase'
        self.USERDATA = 'SSdtIGFjdHVhbGx5IGEgZ29hdC4='
        volume = self.operator_cloud.create_volume(1)
        sot = self.operator_cloud.compute.create_server(
            name=self.NAME,
            flavor_id=self.flavor.id,
            image_id=self.image.id,
            networks='none',
            user_data=self.USERDATA,
            block_device_mapping=[
                {
                    'uuid': volume.id,
                    'source_type': 'volume',
                    'boot_index': 0,
                    'destination_type': 'volume',
                    'delete_on_termination': True,
                    'volume_size': 1,
                },
            ],
        )
        self.operator_cloud.compute.wait_for_server(
            sot, wait=self._wait_for_timeout
        )
        assert isinstance(sot, server.Server)
        self.assertEqual(self.NAME, sot.name)
        self.server = sot

    def tearDown(self):
        sot = self.operator_cloud.compute.delete_server(self.server.id)
        self.operator_cloud.compute.wait_for_delete(
            self.server, wait=self._wait_for_timeout
        )
        self.assertIsNone(sot)
        super().tearDown()

    def test_get(self):
        sot = self.operator_cloud.compute.get_server(self.server.id)
        self.assertIsNotNone(sot.reservation_id)
        self.assertIsNotNone(sot.launch_index)
        self.assertIsNotNone(sot.ramdisk_id)
        self.assertIsNotNone(sot.kernel_id)
        self.assertEqual(self.NAME, sot.hostname)
        self.assertTrue(sot.root_device_name.startswith('/dev'))
        self.assertEqual(self.USERDATA, sot.user_data)
        self.assertTrue(sot.attached_volumes[0]['delete_on_termination'])


class TestServer(ft_base.BaseComputeTest):
    def setUp(self):
        super().setUp()
        self.NAME = self.getUniqueString()
        self.network = None
        self.subnet = None
        self.cidr = '10.99.99.0/16'

        self.network, self.subnet = test_network.create_network(
            self.user_cloud, self.NAME, self.cidr
        )
        self.assertIsNotNone(self.network)

        sot = self.user_cloud.compute.create_server(
            name=self.NAME,
            flavor_id=self.flavor.id,
            image_id=self.image.id,
            networks=[{"uuid": self.network.id}],
        )
        self.user_cloud.compute.wait_for_server(
            sot, wait=self._wait_for_timeout
        )
        assert isinstance(sot, server.Server)
        self.assertEqual(self.NAME, sot.name)
        self.server = sot

    def tearDown(self):
        sot = self.user_cloud.compute.delete_server(self.server.id)
        self.assertIsNone(sot)
        # Need to wait for the stack to go away before network delete
        self.user_cloud.compute.wait_for_delete(
            self.server, wait=self._wait_for_timeout
        )
        test_network.delete_network(self.user_cloud, self.network, self.subnet)
        super().tearDown()

    def test_find(self):
        sot = self.user_cloud.compute.find_server(self.NAME)
        self.assertEqual(self.server.id, sot.id)

    def test_get(self):
        sot = self.user_cloud.compute.get_server(self.server.id)
        self.assertEqual(self.NAME, sot.name)
        self.assertEqual(self.server.id, sot.id)

    def test_list(self):
        names = [o.name for o in self.user_cloud.compute.servers()]
        self.assertIn(self.NAME, names)

    def test_server_metadata(self):
        test_server = self.user_cloud.compute.get_server(self.server.id)

        # get metadata
        test_server = self.user_cloud.compute.get_server_metadata(test_server)
        self.assertFalse(test_server.metadata)

        # set no metadata
        self.user_cloud.compute.set_server_metadata(test_server)
        test_server = self.user_cloud.compute.get_server_metadata(test_server)
        self.assertFalse(test_server.metadata)

        # set empty metadata
        self.user_cloud.compute.set_server_metadata(test_server, k0='')
        server = self.user_cloud.compute.get_server_metadata(test_server)
        self.assertTrue(server.metadata)

        # set metadata
        self.user_cloud.compute.set_server_metadata(test_server, k1='v1')
        test_server = self.user_cloud.compute.get_server_metadata(test_server)
        self.assertTrue(test_server.metadata)
        self.assertEqual(2, len(test_server.metadata))
        self.assertIn('k0', test_server.metadata)
        self.assertEqual('', test_server.metadata['k0'])
        self.assertIn('k1', test_server.metadata)
        self.assertEqual('v1', test_server.metadata['k1'])

        # set more metadata
        self.user_cloud.compute.set_server_metadata(test_server, k2='v2')
        test_server = self.user_cloud.compute.get_server_metadata(test_server)
        self.assertTrue(test_server.metadata)
        self.assertEqual(3, len(test_server.metadata))
        self.assertIn('k0', test_server.metadata)
        self.assertEqual('', test_server.metadata['k0'])
        self.assertIn('k1', test_server.metadata)
        self.assertEqual('v1', test_server.metadata['k1'])
        self.assertIn('k2', test_server.metadata)
        self.assertEqual('v2', test_server.metadata['k2'])

        # update metadata
        self.user_cloud.compute.set_server_metadata(test_server, k1='v1.1')
        test_server = self.user_cloud.compute.get_server_metadata(test_server)
        self.assertTrue(test_server.metadata)
        self.assertEqual(3, len(test_server.metadata))
        self.assertIn('k0', test_server.metadata)
        self.assertEqual('', test_server.metadata['k0'])
        self.assertIn('k1', test_server.metadata)
        self.assertEqual('v1.1', test_server.metadata['k1'])
        self.assertIn('k2', test_server.metadata)
        self.assertEqual('v2', test_server.metadata['k2'])

        # delete metadata
        self.user_cloud.compute.delete_server_metadata(
            test_server, test_server.metadata.keys()
        )
        test_server = self.user_cloud.compute.get_server_metadata(test_server)
        self.assertFalse(test_server.metadata)

    def test_server_remote_console(self):
        console = self.user_cloud.compute.create_server_remote_console(
            self.server, protocol='vnc', type='novnc'
        )
        self.assertEqual('vnc', console.protocol)
        self.assertEqual('novnc', console.type)
        self.assertTrue(console.url.startswith('http'))
