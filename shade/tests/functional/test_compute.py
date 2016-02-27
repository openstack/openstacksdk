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

"""
test_compute
----------------------------------

Functional tests for `shade` compute methods.
"""

from shade.tests.functional import base
from shade.tests.functional.util import pick_flavor, pick_image


class TestCompute(base.BaseFunctionalTestCase):
    def setUp(self):
        super(TestCompute, self).setUp()
        self.flavor = pick_flavor(self.demo_cloud.list_flavors())
        if self.flavor is None:
            self.assertFalse('no sensible flavor available')
        self.image = pick_image(self.demo_cloud.list_images())
        if self.image is None:
            self.assertFalse('no sensible image available')
        self.server_name = self.getUniqueString()

    def _cleanup_servers_and_volumes(self, server_name):
        """Delete the named server and any attached volumes.

        Adding separate cleanup calls for servers and volumes can be tricky
        since they need to be done in the proper order. And sometimes deleting
        a server can start the process of deleting a volume if it is booted
        from that volume. This encapsulates that logic.
        """
        server = self.demo_cloud.get_server(server_name)
        if not server:
            return
        volumes = self.demo_cloud.get_volumes(server)
        self.demo_cloud.delete_server(server.name, wait=True)
        for volume in volumes:
            if volume.status != 'deleting':
                self.demo_cloud.delete_volume(volume.id, wait=True)

    def test_create_and_delete_server(self):
        self.addCleanup(self._cleanup_servers_and_volumes, self.server_name)
        server = self.demo_cloud.create_server(
            name=self.server_name,
            image=self.image,
            flavor=self.flavor,
            wait=True)
        self.assertEqual(self.server_name, server['name'])
        self.assertEqual(self.image.id, server['image']['id'])
        self.assertEqual(self.flavor.id, server['flavor']['id'])
        self.assertIsNotNone(server['adminPass'])
        self.assertTrue(
            self.demo_cloud.delete_server(self.server_name, wait=True))
        self.assertIsNone(self.demo_cloud.get_server(self.server_name))

    def test_create_and_delete_server_with_admin_pass(self):
        self.addCleanup(self._cleanup_servers_and_volumes, self.server_name)
        server = self.demo_cloud.create_server(
            name=self.server_name,
            image=self.image,
            flavor=self.flavor,
            admin_pass='sheiqu9loegahSh',
            wait=True)
        self.assertEqual(self.server_name, server['name'])
        self.assertEqual(self.image.id, server['image']['id'])
        self.assertEqual(self.flavor.id, server['flavor']['id'])
        self.assertEqual(server['adminPass'], 'sheiqu9loegahSh')
        self.assertTrue(
            self.demo_cloud.delete_server(self.server_name, wait=True))
        self.assertIsNone(self.demo_cloud.get_server(self.server_name))

    def test_get_image_id(self):
        self.assertEqual(
            self.image.id, self.demo_cloud.get_image_id(self.image.id))
        self.assertEqual(
            self.image.id, self.demo_cloud.get_image_id(self.image.name))

    def test_get_image_name(self):
        self.assertEqual(
            self.image.name, self.demo_cloud.get_image_name(self.image.id))
        self.assertEqual(
            self.image.name, self.demo_cloud.get_image_name(self.image.name))

    def _assert_volume_attach(self, server, volume_id=None):
        self.assertEqual(self.server_name, server['name'])
        self.assertEqual('', server['image'])
        self.assertEqual(self.flavor.id, server['flavor']['id'])
        volumes = self.demo_cloud.get_volumes(server)
        self.assertEqual(1, len(volumes))
        volume = volumes[0]
        if volume_id:
            self.assertEqual(volume_id, volume['id'])
        else:
            volume_id = volume['id']
        self.assertEqual(1, len(volume['attachments']), 1)
        self.assertEqual(server['id'], volume['attachments'][0]['server_id'])
        return volume_id

    def test_create_boot_from_volume_image(self):
        if not self.demo_cloud.has_service('volume'):
            self.skipTest('volume service not supported by cloud')
        self.addCleanup(self._cleanup_servers_and_volumes, self.server_name)
        server = self.demo_cloud.create_server(
            name=self.server_name,
            image=self.image,
            flavor=self.flavor,
            boot_from_volume=True,
            volume_size=1,
            wait=True)
        volume_id = self._assert_volume_attach(server)
        volume = self.demo_cloud.get_volume(volume_id)
        self.assertIsNotNone(volume)
        self.assertEqual(volume['name'], volume['display_name'])
        self.assertEqual(True, volume['bootable'])
        self.assertEqual(server['id'], volume['attachments'][0]['server_id'])
        self.assertTrue(self.demo_cloud.delete_server(server.id, wait=True))
        self.assertTrue(self.demo_cloud.delete_volume(volume.id, wait=True))
        self.assertIsNone(self.demo_cloud.get_server(server.id))
        self.assertIsNone(self.demo_cloud.get_volume(volume.id))

    def test_create_terminate_volume_image(self):
        if not self.demo_cloud.has_service('volume'):
            self.skipTest('volume service not supported by cloud')
        self.addCleanup(self._cleanup_servers_and_volumes, self.server_name)
        server = self.demo_cloud.create_server(
            name=self.server_name,
            image=self.image,
            flavor=self.flavor,
            boot_from_volume=True,
            terminate_volume=True,
            volume_size=1,
            wait=True)
        volume_id = self._assert_volume_attach(server)
        self.assertTrue(
            self.demo_cloud.delete_server(self.server_name, wait=True))
        volume = self.demo_cloud.get_volume(volume_id)
        # We can either get None (if the volume delete was quick), or a volume
        # that is in the process of being deleted.
        if volume:
            self.assertEquals('deleting', volume.status)
        self.assertIsNone(self.demo_cloud.get_server(self.server_name))

    def test_create_boot_from_volume_preexisting(self):
        if not self.demo_cloud.has_service('volume'):
            self.skipTest('volume service not supported by cloud')
        self.addCleanup(self._cleanup_servers_and_volumes, self.server_name)
        volume = self.demo_cloud.create_volume(
            size=1, name=self.server_name, image=self.image, wait=True)
        server = self.demo_cloud.create_server(
            name=self.server_name,
            image=None,
            flavor=self.flavor,
            boot_volume=volume,
            volume_size=1,
            wait=True)
        volume_id = self._assert_volume_attach(server, volume_id=volume['id'])
        self.assertTrue(
            self.demo_cloud.delete_server(self.server_name, wait=True))
        self.addCleanup(self.demo_cloud.delete_volume, volume_id)
        volume = self.demo_cloud.get_volume(volume_id)
        self.assertIsNotNone(volume)
        self.assertEqual(volume['name'], volume['display_name'])
        self.assertEqual(True, volume['bootable'])
        self.assertEqual([], volume['attachments'])
        self.assertTrue(self.demo_cloud.delete_volume(volume_id))
        self.assertIsNone(self.demo_cloud.get_server(self.server_name))
        self.assertIsNone(self.demo_cloud.get_volume(volume_id))

    def test_create_boot_from_volume_preexisting_terminate(self):
        if not self.demo_cloud.has_service('volume'):
            self.skipTest('volume service not supported by cloud')
        self.addCleanup(self._cleanup_servers_and_volumes, self.server_name)
        volume = self.demo_cloud.create_volume(
            size=1, name=self.server_name, image=self.image, wait=True)
        server = self.demo_cloud.create_server(
            name=self.server_name,
            image=None,
            flavor=self.flavor,
            boot_volume=volume,
            terminate_volume=True,
            volume_size=1,
            wait=True)
        volume_id = self._assert_volume_attach(server, volume_id=volume['id'])
        self.assertTrue(
            self.demo_cloud.delete_server(self.server_name, wait=True))
        volume = self.demo_cloud.get_volume(volume_id)
        # We can either get None (if the volume delete was quick), or a volume
        # that is in the process of being deleted.
        if volume:
            self.assertEquals('deleting', volume.status)
        self.assertIsNone(self.demo_cloud.get_server(self.server_name))

    def test_create_image_snapshot_wait_active(self):
        self.addCleanup(self._cleanup_servers_and_volumes, self.server_name)
        server = self.demo_cloud.create_server(
            name=self.server_name,
            image=self.image,
            flavor=self.flavor,
            admin_pass='sheiqu9loegahSh',
            wait=True)
        image = self.demo_cloud.create_image_snapshot('test-snapshot', server,
                                                      wait=True)
        self.addCleanup(self.demo_cloud.delete_image, image['id'])
        self.assertEqual('active', image['status'])
