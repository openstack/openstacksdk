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

from openstack.tests.functional import base


class TestProjectCleanup(base.BaseFunctionalTest):
    _wait_for_timeout_key = 'OPENSTACKSDK_FUNC_TEST_TIMEOUT_CLEANUP'

    def setUp(self):
        super(TestProjectCleanup, self).setUp()
        if not self.user_cloud_alt:
            self.skipTest("Alternate demo cloud is required for this test")

        self.conn = self.user_cloud_alt
        self.network_name = self.getUniqueString('network')

    def _create_network_resources(self):
        conn = self.conn
        self.net = conn.network.create_network(
            name=self.network_name,
        )
        self.subnet = conn.network.create_subnet(
            name=self.getUniqueString('subnet'),
            network_id=self.net.id,
            cidr='192.169.1.0/24',
            ip_version=4,
        )
        self.router = conn.network.create_router(
            name=self.getUniqueString('router')
        )
        conn.network.add_interface_to_router(
            self.router.id, subnet_id=self.subnet.id
        )

    def test_cleanup(self):
        self._create_network_resources()
        status_queue = queue.Queue()

        # First round - check no resources are old enough
        self.conn.project_cleanup(
            dry_run=True,
            wait_timeout=120,
            status_queue=status_queue,
            filters={'created_at': '2000-01-01'},
        )

        self.assertTrue(status_queue.empty())

        # Second round - resource evaluation function return false, ensure
        # nothing identified
        self.conn.project_cleanup(
            dry_run=True,
            wait_timeout=120,
            status_queue=status_queue,
            filters={'created_at': '2200-01-01'},
            resource_evaluation_fn=lambda x, y, z: False,
        )

        self.assertTrue(status_queue.empty())

        # Third round - filters set too low
        self.conn.project_cleanup(
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
        self.conn.project_cleanup(
            dry_run=True, wait_timeout=120, status_queue=status_queue
        )

        objects = []
        while not status_queue.empty():
            objects.append(status_queue.get())

        net_names = list(obj.name for obj in objects)
        self.assertIn(self.network_name, net_names)

        # Ensure network still exists
        net = self.conn.network.get_network(self.net.id)
        self.assertEqual(net.name, self.net.name)

        # Last round - do a real cleanup
        self.conn.project_cleanup(
            dry_run=False, wait_timeout=600, status_queue=status_queue
        )

        objects = []
        while not status_queue.empty():
            objects.append(status_queue.get())

        nets = self.conn.network.networks()
        net_names = list(obj.name for obj in nets)
        # Since we might not have enough privs to drop all nets - ensure
        # we do not have our known one
        self.assertNotIn(self.network_name, net_names)

    def test_block_storage_cleanup(self):
        if not self.user_cloud.has_service('object-store'):
            self.skipTest('Object service is requred, but not available')

        status_queue = queue.Queue()

        vol = self.conn.block_storage.create_volume(name='vol1', size='1')
        self.conn.block_storage.wait_for_status(vol)
        s1 = self.conn.block_storage.create_snapshot(volume_id=vol.id)
        self.conn.block_storage.wait_for_status(s1)
        b1 = self.conn.block_storage.create_backup(volume_id=vol.id)
        self.conn.block_storage.wait_for_status(b1)
        b2 = self.conn.block_storage.create_backup(
            volume_id=vol.id, is_incremental=True, snapshot_id=s1.id
        )
        self.conn.block_storage.wait_for_status(b2)
        b3 = self.conn.block_storage.create_backup(
            volume_id=vol.id, is_incremental=True, snapshot_id=s1.id
        )
        self.conn.block_storage.wait_for_status(b3)

        # First round - check no resources are old enough
        self.conn.project_cleanup(
            dry_run=True,
            wait_timeout=120,
            status_queue=status_queue,
            filters={'created_at': '2000-01-01'},
        )

        self.assertTrue(status_queue.empty())

        # Second round - resource evaluation function return false, ensure
        # nothing identified
        self.conn.project_cleanup(
            dry_run=True,
            wait_timeout=120,
            status_queue=status_queue,
            filters={'created_at': '2200-01-01'},
            resource_evaluation_fn=lambda x, y, z: False,
        )

        self.assertTrue(status_queue.empty())

        # Third round - filters set too low
        self.conn.project_cleanup(
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
        self.conn.project_cleanup(
            dry_run=True, wait_timeout=120, status_queue=status_queue
        )

        objects = []
        while not status_queue.empty():
            objects.append(status_queue.get())

        vol_ids = list(obj.id for obj in objects)
        self.assertIn(vol.id, vol_ids)

        # Ensure volume still exists
        vol_check = self.conn.block_storage.get_volume(vol.id)
        self.assertEqual(vol.name, vol_check.name)

        # Last round - do a real cleanup
        self.conn.project_cleanup(
            dry_run=False, wait_timeout=600, status_queue=status_queue
        )
        # Ensure no backups remain
        self.assertEqual(0, len(list(self.conn.block_storage.backups())))
        # Ensure no snapshots remain
        self.assertEqual(0, len(list(self.conn.block_storage.snapshots())))

    def test_cleanup_swift(self):
        if not self.user_cloud.has_service('object-store'):
            self.skipTest('Object service is requred, but not available')

        status_queue = queue.Queue()
        self.conn.object_store.create_container('test_cleanup')
        for i in range(1, 10):
            self.conn.object_store.create_object(
                "test_cleanup", f"test{i}", data="test{i}"
            )

        # First round - check no resources are old enough
        self.conn.project_cleanup(
            dry_run=True,
            wait_timeout=120,
            status_queue=status_queue,
            filters={'updated_at': '2000-01-01'},
        )

        self.assertTrue(status_queue.empty())

        # Second round - filters set too low
        self.conn.project_cleanup(
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
        obj = self.conn.object_store.get_object("test1", "test_cleanup")
        self.assertIsNotNone(obj)

        # Last round - do a real cleanup
        self.conn.project_cleanup(
            dry_run=False, wait_timeout=600, status_queue=status_queue
        )

        objects.clear()
        while not status_queue.empty():
            objects.append(status_queue.get())
        self.assertIsNone(self.conn.get_container('test_container'))
