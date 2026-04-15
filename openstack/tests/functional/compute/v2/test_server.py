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

from openstack.compute.v2 import server as _server
from openstack.tests.functional.compute.v2 import base
from openstack.tests.functional.network.v2 import test_network


class TestServerAdmin(base.BaseComputeTest):
    def setUp(self):
        super().setUp()
        self.server_name = 'needstobeshortandlowercase'
        self.user_data = 'SSdtIGFjdHVhbGx5IGEgZ29hdC4='

    def _delete_server(self, server):
        sot = self.admin_compute_client.delete_server(server.id)
        self.admin_compute_client.wait_for_delete(
            server, wait=self._wait_for_timeout
        )
        self.assertIsNone(sot)

    def test_server(self):
        # create server with volume
        volume = self.admin_block_storage_client.create_volume(size=1)
        self.admin_block_storage_client.wait_for_status(
            volume, wait=self._wait_for_timeout
        )
        server = self.admin_compute_client.create_server(
            name=self.server_name,
            flavor_id=self.flavor.id,
            image_id=self.image.id,
            networks='none',
            user_data=self.user_data,
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
        self.admin_compute_client.wait_for_server(
            server, wait=self._wait_for_timeout
        )
        self.assertIsInstance(server, _server.Server)
        self.assertEqual(self.server_name, server.name)
        self.addCleanup(self._delete_server, server)

        # get server details (admin-specific fields)

        server = self.admin_compute_client.get_server(server.id)
        self.assertIsNotNone(server.reservation_id)
        self.assertIsNotNone(server.launch_index)
        self.assertIsNotNone(server.ramdisk_id)
        self.assertIsNotNone(server.kernel_id)
        self.assertEqual(self.server_name, server.hostname)
        self.assertTrue(server.root_device_name.startswith('/dev'))
        self.assertEqual(self.user_data, server.user_data)
        self.assertTrue(server.attached_volumes[0]['delete_on_termination'])


class TestServer(base.BaseComputeTest):
    def setUp(self):
        super().setUp()
        self.server_name = self.getUniqueString()
        self.cidr = '10.99.99.0/16'

        # create network for server

        self.network, self.subnet = test_network.create_network(
            self.user_cloud, self.server_name, self.cidr
        )
        self.assertIsNotNone(self.network)
        self.addCleanup(self._delete_network, self.network, self.subnet)

    def _delete_server(self, server):
        sot = self.compute_client.delete_server(server.id)
        self.assertIsNone(sot)
        # Need to wait for the stack to go away before network delete
        self.compute_client.wait_for_delete(
            server, wait=self._wait_for_timeout
        )

    def _delete_network(self, network, subnet):
        test_network.delete_network(self.user_cloud, network, subnet)

    def test_server(self):
        # create server

        self.server = self.compute_client.create_server(
            name=self.server_name,
            flavor_id=self.flavor.id,
            image_id=self.image.id,
            networks=[{"uuid": self.network.id}],
        )
        self.compute_client.wait_for_server(
            self.server, wait=self._wait_for_timeout
        )
        self.addCleanup(self._delete_server, self.server)
        self.assertIsInstance(self.server, _server.Server)
        self.assertEqual(self.server_name, self.server.name)

        # find server by name

        server = self.compute_client.find_server(
            self.server_name, ignore_missing=False
        )
        self.assertEqual(self.server.id, server.id)

        # get server by ID

        server = self.compute_client.get_server(self.server.id)
        self.assertEqual(self.server_name, server.name)
        self.assertEqual(self.server.id, server.id)

        # list servers

        server = self.compute_client.servers()
        self.assertIn(self.server_name, {x.name for x in server})

    def test_server_metadata(self):
        # create server

        server = self.compute_client.create_server(
            name=self.server_name,
            flavor_id=self.flavor.id,
            image_id=self.image.id,
            networks=[{"uuid": self.network.id}],
        )
        self.compute_client.wait_for_server(
            server, wait=self._wait_for_timeout
        )
        self.assertIsInstance(server, _server.Server)
        self.addCleanup(self._delete_server, server)

        # get metadata (should be empty initially)

        server = self.compute_client.get_server_metadata(server)
        self.assertFalse(server.metadata)

        # set no metadata

        self.compute_client.set_server_metadata(server)
        server = self.compute_client.get_server_metadata(server)
        self.assertFalse(server.metadata)

        # set empty metadata

        self.compute_client.set_server_metadata(server, k0='')
        server = self.compute_client.get_server_metadata(server)
        self.assertTrue(server.metadata)

        # set metadata

        self.compute_client.set_server_metadata(server, k1='v1')
        server = self.compute_client.get_server_metadata(server)
        self.assertTrue(server.metadata)
        self.assertEqual(2, len(server.metadata))
        self.assertIn('k0', server.metadata)
        self.assertEqual('', server.metadata['k0'])
        self.assertIn('k1', server.metadata)
        self.assertEqual('v1', server.metadata['k1'])

        # set more metadata

        self.compute_client.set_server_metadata(server, k2='v2')
        server = self.compute_client.get_server_metadata(server)
        self.assertTrue(server.metadata)
        self.assertEqual(3, len(server.metadata))
        self.assertIn('k0', server.metadata)
        self.assertEqual('', server.metadata['k0'])
        self.assertIn('k1', server.metadata)
        self.assertEqual('v1', server.metadata['k1'])
        self.assertIn('k2', server.metadata)
        self.assertEqual('v2', server.metadata['k2'])

        # update metadata

        self.compute_client.set_server_metadata(server, k1='v1.1')
        server = self.compute_client.get_server_metadata(server)
        self.assertTrue(server.metadata)
        self.assertEqual(3, len(server.metadata))
        self.assertIn('k0', server.metadata)
        self.assertEqual('', server.metadata['k0'])
        self.assertIn('k1', server.metadata)
        self.assertEqual('v1.1', server.metadata['k1'])
        self.assertIn('k2', server.metadata)
        self.assertEqual('v2', server.metadata['k2'])

        # delete all metadata (cleanup)

        self.compute_client.delete_server_metadata(
            server, server.metadata.keys()
        )
        server = self.compute_client.get_server_metadata(server)
        self.assertFalse(server.metadata)

    def test_server_remote_console(self):
        # create network for server

        network, subnet = test_network.create_network(
            self.user_cloud, self.server_name, self.cidr
        )
        self.assertIsNotNone(network)
        self.addCleanup(self._delete_network, network, subnet)

        # create server

        server = self.compute_client.create_server(
            name=self.server_name,
            flavor_id=self.flavor.id,
            image_id=self.image.id,
            networks=[{"uuid": network.id}],
        )
        self.compute_client.wait_for_server(
            server, wait=self._wait_for_timeout
        )
        self.assertIsInstance(server, _server.Server)
        self.addCleanup(self._delete_server, server)

        # create remote console

        console = self.compute_client.create_server_remote_console(
            server, protocol='vnc', type='novnc'
        )
        self.assertEqual('vnc', console.protocol)
        self.assertEqual('novnc', console.type)
        self.assertTrue(console.url.startswith('http'))
