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
test_project_cleanup
----------------------------------

Functional tests for project cleanup methods.
"""

import queue

from openstack.network.v2 import network as _network
from openstack import resource
from openstack.tests.functional import base


class TestProjectCleanup(base.BaseFunctionalTest):
    _wait_for_timeout_key = 'OPENSTACKSDK_FUNC_TEST_TIMEOUT_CLEANUP'

    def setUp(self):
        super().setUp()
        if not self.user_cloud_alt:
            self.skipTest("Alternate demo cloud is required for this test")

        self.network_name = self.getUniqueString('network')

    def _create_network_resources(self):
        self.net = self.user_cloud_alt.network.create_network(
            name=self.network_name,
        )
        self.subnet = self.user_cloud_alt.network.create_subnet(
            name=self.getUniqueString('subnet'),
            network_id=self.net.id,
            cidr='192.169.1.0/24',
            ip_version=4,
        )
        self.router = self.user_cloud_alt.network.create_router(
            name=self.getUniqueString('router')
        )
        self.user_cloud_alt.network.add_interface_to_router(
            self.router.id, subnet_id=self.subnet.id
        )

    def test_cleanup(self):
        self._create_network_resources()
        status_queue: queue.Queue[resource.Resource] = queue.Queue()

        # First round - check no resources are old enough
        self.user_cloud_alt.project_cleanup(
            dry_run=True,
            wait_timeout=120,
            status_queue=status_queue,
            filters={'created_at': '2000-01-01'},
        )

        self.assertTrue(status_queue.empty())

        # Second round - resource evaluation function return false, ensure
        # nothing identified
        self.user_cloud_alt.project_cleanup(
            dry_run=True,
            wait_timeout=120,
            status_queue=status_queue,
            filters={'created_at': '2200-01-01'},
            resource_evaluation_fn=lambda x, y, z: False,
        )

        self.assertTrue(status_queue.empty())

        # Third round - filters set too low
        self.user_cloud_alt.project_cleanup(
            dry_run=True,
            wait_timeout=120,
            status_queue=status_queue,
            filters={'created_at': '2200-01-01'},
        )

        objects = []
        while not status_queue.empty():
            objects.append(status_queue.get())

        # At least known networks should be identified
        net_names = list(obj.name for obj in objects)
        self.assertIn(self.network_name, net_names)

        # Fourth round - dry run with no filters, ensure everything identified
        self.user_cloud_alt.project_cleanup(
            dry_run=True, wait_timeout=120, status_queue=status_queue
        )

        objects = []
        while not status_queue.empty():
            objects.append(status_queue.get())

        net_names = list(obj.name for obj in objects)
        self.assertIn(self.network_name, net_names)

        # Ensure network still exists
        net = self.user_cloud_alt.network.get_network(self.net.id)
        self.assertEqual(net.name, self.net.name)

        # Last round - do a real cleanup
        self.user_cloud_alt.project_cleanup(
            dry_run=False, wait_timeout=600, status_queue=status_queue
        )

        objects = []
        while not status_queue.empty():
            objects.append(status_queue.get())

        nets = self.user_cloud_alt.network.networks()
        net_names = list(obj.name for obj in nets)
        # Since we might not have enough privs to drop all nets - ensure
        # we do not have our known one
        self.assertNotIn(self.network_name, net_names)

    def test_block_storage_cleanup(self):
        if not self.user_cloud.has_service('object-store'):
            self.skipTest('Object service is requred, but not available')

        status_queue: queue.Queue[resource.Resource] = queue.Queue()

        vol = self.user_cloud_alt.block_storage.create_volume(
            name='vol1', size='1'
        )
        self.user_cloud_alt.block_storage.wait_for_status(vol)
        s1 = self.user_cloud_alt.block_storage.create_snapshot(
            volume_id=vol.id
        )
        self.user_cloud_alt.block_storage.wait_for_status(s1)
        b1 = self.user_cloud_alt.block_storage.create_backup(volume_id=vol.id)
        self.user_cloud_alt.block_storage.wait_for_status(b1)
        b2 = self.user_cloud_alt.block_storage.create_backup(
            volume_id=vol.id, is_incremental=True, snapshot_id=s1.id
        )
        self.user_cloud_alt.block_storage.wait_for_status(b2)
        b3 = self.user_cloud_alt.block_storage.create_backup(
            volume_id=vol.id, is_incremental=True, snapshot_id=s1.id
        )
        self.user_cloud_alt.block_storage.wait_for_status(b3)

        # First round - check no resources are old enough
        self.user_cloud_alt.project_cleanup(
            dry_run=True,
            wait_timeout=120,
            status_queue=status_queue,
            filters={'created_at': '2000-01-01'},
        )

        self.assertTrue(status_queue.empty())

        # Second round - resource evaluation function return false, ensure
        # nothing identified
        self.user_cloud_alt.project_cleanup(
            dry_run=True,
            wait_timeout=120,
            status_queue=status_queue,
            filters={'created_at': '2200-01-01'},
            resource_evaluation_fn=lambda x, y, z: False,
        )

        self.assertTrue(status_queue.empty())

        # Third round - filters set too low
        self.user_cloud_alt.project_cleanup(
            dry_run=True,
            wait_timeout=120,
            status_queue=status_queue,
            filters={'created_at': '2200-01-01'},
        )

        objects = []
        while not status_queue.empty():
            objects.append(status_queue.get())

        # At least known networks should be identified
        volumes = list(obj.id for obj in objects)
        self.assertIn(vol.id, volumes)

        # Fourth round - dry run with no filters, ensure everything identified
        self.user_cloud_alt.project_cleanup(
            dry_run=True, wait_timeout=120, status_queue=status_queue
        )

        objects = []
        while not status_queue.empty():
            objects.append(status_queue.get())

        vol_ids = list(obj.id for obj in objects)
        self.assertIn(vol.id, vol_ids)

        # Ensure volume still exists
        vol_check = self.user_cloud_alt.block_storage.get_volume(vol.id)
        self.assertEqual(vol.name, vol_check.name)

        # Last round - do a real cleanup
        self.user_cloud_alt.project_cleanup(
            dry_run=False, wait_timeout=600, status_queue=status_queue
        )
        # Ensure no backups remain
        self.assertEqual(
            0, len(list(self.user_cloud_alt.block_storage.backups()))
        )
        # Ensure no snapshots remain
        self.assertEqual(
            0, len(list(self.user_cloud_alt.block_storage.snapshots()))
        )

    def test_cleanup_swift(self):
        if not self.user_cloud.has_service('object-store'):
            self.skipTest('Object service is requred, but not available')

        status_queue: queue.Queue[resource.Resource] = queue.Queue()

        self.user_cloud_alt.object_store.create_container('test_cleanup')
        for i in range(1, 10):
            self.user_cloud_alt.object_store.create_object(
                "test_cleanup", f"test{i}", data="test{i}"
            )

        # First round - check no resources are old enough
        self.user_cloud_alt.project_cleanup(
            dry_run=True,
            wait_timeout=120,
            status_queue=status_queue,
            filters={'updated_at': '2000-01-01'},
        )

        self.assertTrue(status_queue.empty())

        # Second round - filters set too low
        self.user_cloud_alt.project_cleanup(
            dry_run=True,
            wait_timeout=120,
            status_queue=status_queue,
            filters={'updated_at': '2200-01-01'},
        )
        objects = []
        while not status_queue.empty():
            objects.append(status_queue.get())

        # At least known objects should be identified
        obj_names = list(obj.name for obj in objects)
        self.assertIn('test1', obj_names)

        # Ensure object still exists
        obj = self.user_cloud_alt.object_store.get_object(
            "test1", "test_cleanup"
        )
        self.assertIsNotNone(obj)

        # Last round - do a real cleanup
        self.user_cloud_alt.project_cleanup(
            dry_run=False, wait_timeout=600, status_queue=status_queue
        )

        objects.clear()
        while not status_queue.empty():
            objects.append(status_queue.get())
        self.assertIsNone(self.user_cloud_alt.get_container('test_container'))

    def test_cleanup_vpnaas(self):
        if not list(
            self.user_cloud_alt.network.service_providers(service_type="VPN")
        ):
            self.skipTest("VPNaaS plugin is requred, but not available")

        status_queue: queue.Queue[resource.Resource] = queue.Queue()

        # Find available external networks and use one
        for network in self.user_cloud_alt.network.networks():
            if network.is_router_external:
                external_network: _network.Network = network
                break
        else:
            self.skipTest("External network is required, but not available")

        # Create left network resources
        network_left = self.user_cloud_alt.network.create_network(
            name="network_left"
        )
        subnet_left = self.user_cloud_alt.network.create_subnet(
            name="subnet_left",
            network_id=network_left.id,
            cidr="192.168.1.0/24",
            ip_version=4,
        )
        router_left = self.user_cloud_alt.network.create_router(
            name="router_left"
        )
        self.user_cloud_alt.network.add_interface_to_router(
            router=router_left.id, subnet_id=subnet_left.id
        )
        router_left = self.user_cloud_alt.network.update_router(
            router_left,
            external_gateway_info={"network_id": external_network.id},
        )

        # Create right network resources
        network_right = self.user_cloud_alt.network.create_network(
            name="network_right"
        )
        subnet_right = self.user_cloud_alt.network.create_subnet(
            name="subnet_right",
            network_id=network_right.id,
            cidr="192.168.2.0/24",
            ip_version=4,
        )
        router_right = self.user_cloud_alt.network.create_router(
            name="router_right"
        )
        self.user_cloud_alt.network.add_interface_to_router(
            router=router_right.id, subnet_id=subnet_right.id
        )
        router_right = self.user_cloud_alt.network.update_router(
            router_right,
            external_gateway_info={"network_id": external_network.id},
        )

        # Create VPNaaS resources
        ike_policy = self.user_cloud_alt.network.create_vpn_ike_policy(
            name="ike_policy"
        )
        ipsec_policy = self.user_cloud_alt.network.create_vpn_ipsec_policy(
            name="ipsec_policy"
        )

        vpn_service = self.user_cloud_alt.network.create_vpn_service(
            name="vpn_service", router_id=router_left.id
        )

        ep_group_local = self.user_cloud_alt.network.create_vpn_endpoint_group(
            name="endpoint_group_local",
            type="subnet",
            endpoints=[subnet_left.id],
        )
        ep_group_peer = self.user_cloud_alt.network.create_vpn_endpoint_group(
            name="endpoint_group_peer",
            type="cidr",
            endpoints=[subnet_right.cidr],
        )

        router_right_ip = router_right.external_gateway_info[
            'external_fixed_ips'
        ][0]['ip_address']
        ipsec_site_conn = (
            self.user_cloud_alt.network.create_vpn_ipsec_site_connection(
                name="ipsec_site_connection",
                vpnservice_id=vpn_service.id,
                ikepolicy_id=ike_policy.id,
                ipsecpolicy_id=ipsec_policy.id,
                local_ep_group_id=ep_group_local.id,
                peer_ep_group_id=ep_group_peer.id,
                psk="test",
                peer_address=router_right_ip,
                peer_id=router_right_ip,
            )
        )

        # First round - check no resources are old enough
        self.user_cloud_alt.project_cleanup(
            dry_run=True,
            wait_timeout=120,
            status_queue=status_queue,
            filters={'created_at': '2000-01-01'},
        )
        self.assertTrue(status_queue.empty())

        # Second round - resource evaluation function return false, ensure
        # nothing identified
        self.user_cloud_alt.project_cleanup(
            dry_run=True,
            wait_timeout=120,
            status_queue=status_queue,
            filters={'created_at': '2200-01-01'},
            resource_evaluation_fn=lambda x, y, z: False,
        )
        self.assertTrue(status_queue.empty())

        # Third round - filters set too low
        self.user_cloud_alt.project_cleanup(
            dry_run=True,
            wait_timeout=120,
            status_queue=status_queue,
            filters={'created_at': '2200-01-01'},
        )
        objects = []
        while not status_queue.empty():
            objects.append(status_queue.get())

        # VPN resources do not have a created_at property
        # Check for the network instead
        resource_ids = list(obj.id for obj in objects)
        self.assertIn(network_left.id, resource_ids)

        # Fourth round - dry run with no filters, ensure everything identified
        self.user_cloud_alt.project_cleanup(
            dry_run=True, wait_timeout=120, status_queue=status_queue
        )
        objects = []
        while not status_queue.empty():
            objects.append(status_queue.get())

        resource_ids = list(obj.id for obj in objects)
        self.assertIn(ipsec_site_conn.id, resource_ids)

        # Ensure vpn resources still exist
        site_conn_check = (
            self.user_cloud_alt.network.get_vpn_ipsec_site_connection(
                ipsec_site_conn.id
            )
        )
        self.assertEqual(site_conn_check.name, ipsec_site_conn.name)

        # Last round - do a real cleanup
        self.user_cloud_alt.project_cleanup(
            dry_run=False, wait_timeout=600, status_queue=status_queue
        )
        # Ensure no VPN resources remain
        self.assertEqual(
            0, len(list(self.user_cloud_alt.network.vpn_ike_policies()))
        )
        self.assertEqual(
            0, len(list(self.user_cloud_alt.network.vpn_ipsec_policies()))
        )
        self.assertEqual(
            0, len(list(self.user_cloud_alt.network.vpn_services()))
        )
        self.assertEqual(
            0, len(list(self.user_cloud_alt.network.vpn_endpoint_groups()))
        )
        self.assertEqual(
            0,
            len(
                list(self.user_cloud_alt.network.vpn_ipsec_site_connections())
            ),
        )
