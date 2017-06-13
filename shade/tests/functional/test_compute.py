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

import six

from shade import exc
from shade.tests.functional import base
from shade.tests.functional.util import pick_flavor
from shade import _utils


class TestCompute(base.BaseFunctionalTestCase):
    def setUp(self):
        # OS_TEST_TIMEOUT is 60 sec by default
        # but on a bad day, test_attach_detach_volume can take more time.
        self.TIMEOUT_SCALING_FACTOR = 1.5

        super(TestCompute, self).setUp()
        self.flavor = pick_flavor(
            self.user_cloud.list_flavors(get_extra=False))
        if self.flavor is None:
            self.assertFalse('no sensible flavor available')
        self.image = self.pick_image()
        self.server_name = self.getUniqueString()

    def _cleanup_servers_and_volumes(self, server_name):
        """Delete the named server and any attached volumes.

        Adding separate cleanup calls for servers and volumes can be tricky
        since they need to be done in the proper order. And sometimes deleting
        a server can start the process of deleting a volume if it is booted
        from that volume. This encapsulates that logic.
        """
        server = self.user_cloud.get_server(server_name)
        if not server:
            return
        volumes = self.user_cloud.get_volumes(server)
        self.user_cloud.delete_server(server.name, wait=True)
        for volume in volumes:
            if volume.status != 'deleting':
                self.user_cloud.delete_volume(volume.id, wait=True)

    def test_create_and_delete_server(self):
        self.addCleanup(self._cleanup_servers_and_volumes, self.server_name)
        server = self.user_cloud.create_server(
            name=self.server_name,
            image=self.image,
            flavor=self.flavor,
            wait=True)
        self.assertEqual(self.server_name, server['name'])
        self.assertEqual(self.image.id, server['image']['id'])
        self.assertEqual(self.flavor.id, server['flavor']['id'])
        self.assertIsNotNone(server['adminPass'])
        self.assertTrue(
            self.user_cloud.delete_server(self.server_name, wait=True))
        self.assertIsNone(self.user_cloud.get_server(self.server_name))

    def test_attach_detach_volume(self):
        server_name = self.getUniqueString()
        self.addCleanup(self._cleanup_servers_and_volumes, server_name)
        server = self.user_cloud.create_server(
            name=server_name, image=self.image, flavor=self.flavor,
            wait=True)
        volume = self.user_cloud.create_volume(1)
        vol_attachment = self.user_cloud.attach_volume(server, volume)
        for key in ('device', 'serverId', 'volumeId'):
            self.assertIn(key, vol_attachment)
            self.assertTrue(vol_attachment[key])  # assert string is not empty
        self.assertIsNone(self.user_cloud.detach_volume(server, volume))

    def test_list_all_servers(self):
        self.addCleanup(self._cleanup_servers_and_volumes, self.server_name)
        server = self.user_cloud.create_server(
            name=self.server_name,
            image=self.image,
            flavor=self.flavor,
            wait=True)
        # We're going to get servers from other tests, but that's ok, as long
        # as we get the server we created with the demo user.
        found_server = False
        for s in self.operator_cloud.list_servers(all_projects=True):
            if s.name == server.name:
                found_server = True
        self.assertTrue(found_server)

    def test_list_all_servers_bad_permissions(self):
        # Normal users are not allowed to pass all_projects=True
        self.assertRaises(
            exc.OpenStackCloudException,
            self.user_cloud.list_servers,
            all_projects=True)

    def test_create_server_image_flavor_dict(self):
        self.addCleanup(self._cleanup_servers_and_volumes, self.server_name)
        server = self.user_cloud.create_server(
            name=self.server_name,
            image={'id': self.image.id},
            flavor={'id': self.flavor.id},
            wait=True)
        self.assertEqual(self.server_name, server['name'])
        self.assertEqual(self.image.id, server['image']['id'])
        self.assertEqual(self.flavor.id, server['flavor']['id'])
        self.assertIsNotNone(server['adminPass'])
        self.assertTrue(
            self.user_cloud.delete_server(self.server_name, wait=True))
        self.assertIsNone(self.user_cloud.get_server(self.server_name))

    def test_get_server_console(self):
        self.addCleanup(self._cleanup_servers_and_volumes, self.server_name)
        server = self.user_cloud.create_server(
            name=self.server_name,
            image=self.image,
            flavor=self.flavor,
            wait=True)
        for _ in _utils._iterate_timeout(
                5, "Did not get more than 0 lines in the console log"):
            log = self.user_cloud.get_server_console(server=server)
            self.assertTrue(isinstance(log, six.string_types))
            if len(log) > 0:
                break

    def test_get_server_console_name_or_id(self):
        self.addCleanup(self._cleanup_servers_and_volumes, self.server_name)
        self.user_cloud.create_server(
            name=self.server_name,
            image=self.image,
            flavor=self.flavor,
            wait=True)
        for _ in _utils._iterate_timeout(
                5, "Did not get more than 0 lines in the console log"):
            log = self.user_cloud.get_server_console(server=self.server_name)
            self.assertTrue(isinstance(log, six.string_types))
            if len(log) > 0:
                break

    def test_list_availability_zone_names(self):
        self.assertEqual(
            ['nova'], self.user_cloud.list_availability_zone_names())

    def test_get_server_console_bad_server(self):
        self.assertRaises(
            exc.OpenStackCloudException,
            self.user_cloud.get_server_console,
            server=self.server_name)

    def test_create_and_delete_server_with_admin_pass(self):
        self.addCleanup(self._cleanup_servers_and_volumes, self.server_name)
        server = self.user_cloud.create_server(
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
            self.user_cloud.delete_server(self.server_name, wait=True))
        self.assertIsNone(self.user_cloud.get_server(self.server_name))

    def test_get_image_id(self):
        self.assertEqual(
            self.image.id, self.user_cloud.get_image_id(self.image.id))
        self.assertEqual(
            self.image.id, self.user_cloud.get_image_id(self.image.name))

    def test_get_image_name(self):
        self.assertEqual(
            self.image.name, self.user_cloud.get_image_name(self.image.id))
        self.assertEqual(
            self.image.name, self.user_cloud.get_image_name(self.image.name))

    def _assert_volume_attach(self, server, volume_id=None, image=''):
        self.assertEqual(self.server_name, server['name'])
        self.assertEqual(image, server['image'])
        self.assertEqual(self.flavor.id, server['flavor']['id'])
        volumes = self.user_cloud.get_volumes(server)
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
        if not self.user_cloud.has_service('volume'):
            self.skipTest('volume service not supported by cloud')
        self.addCleanup(self._cleanup_servers_and_volumes, self.server_name)
        server = self.user_cloud.create_server(
            name=self.server_name,
            image=self.image,
            flavor=self.flavor,
            boot_from_volume=True,
            volume_size=1,
            wait=True)
        volume_id = self._assert_volume_attach(server)
        volume = self.user_cloud.get_volume(volume_id)
        self.assertIsNotNone(volume)
        self.assertEqual(volume['name'], volume['display_name'])
        self.assertEqual(True, volume['bootable'])
        self.assertEqual(server['id'], volume['attachments'][0]['server_id'])
        self.assertTrue(self.user_cloud.delete_server(server.id, wait=True))
        self._wait_for_detach(volume.id)
        self.assertTrue(self.user_cloud.delete_volume(volume.id, wait=True))
        self.assertIsNone(self.user_cloud.get_server(server.id))
        self.assertIsNone(self.user_cloud.get_volume(volume.id))

    def _wait_for_detach(self, volume_id):
        # Volumes do not show up as unattached for a bit immediately after
        # deleting a server that had had a volume attached. Yay for eventual
        # consistency!
        for count in _utils._iterate_timeout(
                60,
                'Timeout waiting for volume {volume_id} to detach'.format(
                    volume_id=volume_id)):
            volume = self.user_cloud.get_volume(volume_id)
            if volume.status in (
                    'available', 'error',
                    'error_restoring', 'error_extending'):
                return

    def test_create_terminate_volume_image(self):
        if not self.user_cloud.has_service('volume'):
            self.skipTest('volume service not supported by cloud')
        self.addCleanup(self._cleanup_servers_and_volumes, self.server_name)
        server = self.user_cloud.create_server(
            name=self.server_name,
            image=self.image,
            flavor=self.flavor,
            boot_from_volume=True,
            terminate_volume=True,
            volume_size=1,
            wait=True)
        volume_id = self._assert_volume_attach(server)
        self.assertTrue(
            self.user_cloud.delete_server(self.server_name, wait=True))
        volume = self.user_cloud.get_volume(volume_id)
        # We can either get None (if the volume delete was quick), or a volume
        # that is in the process of being deleted.
        if volume:
            self.assertEqual('deleting', volume.status)
        self.assertIsNone(self.user_cloud.get_server(self.server_name))

    def test_create_boot_from_volume_preexisting(self):
        if not self.user_cloud.has_service('volume'):
            self.skipTest('volume service not supported by cloud')
        self.addCleanup(self._cleanup_servers_and_volumes, self.server_name)
        volume = self.user_cloud.create_volume(
            size=1, name=self.server_name, image=self.image, wait=True)
        self.addCleanup(self.user_cloud.delete_volume, volume.id)
        server = self.user_cloud.create_server(
            name=self.server_name,
            image=None,
            flavor=self.flavor,
            boot_volume=volume,
            volume_size=1,
            wait=True)
        volume_id = self._assert_volume_attach(server, volume_id=volume['id'])
        self.assertTrue(
            self.user_cloud.delete_server(self.server_name, wait=True))
        volume = self.user_cloud.get_volume(volume_id)
        self.assertIsNotNone(volume)
        self.assertEqual(volume['name'], volume['display_name'])
        self.assertEqual(True, volume['bootable'])
        self.assertEqual([], volume['attachments'])
        self._wait_for_detach(volume.id)
        self.assertTrue(self.user_cloud.delete_volume(volume_id))
        self.assertIsNone(self.user_cloud.get_server(self.server_name))
        self.assertIsNone(self.user_cloud.get_volume(volume_id))

    def test_create_boot_attach_volume(self):
        if not self.user_cloud.has_service('volume'):
            self.skipTest('volume service not supported by cloud')
        self.addCleanup(self._cleanup_servers_and_volumes, self.server_name)
        volume = self.user_cloud.create_volume(
            size=1, name=self.server_name, image=self.image, wait=True)
        self.addCleanup(self.user_cloud.delete_volume, volume['id'])
        server = self.user_cloud.create_server(
            name=self.server_name,
            flavor=self.flavor,
            image=self.image,
            boot_from_volume=False,
            volumes=[volume],
            wait=True)
        volume_id = self._assert_volume_attach(
            server, volume_id=volume['id'], image={'id': self.image['id']})
        self.assertTrue(
            self.user_cloud.delete_server(self.server_name, wait=True))
        volume = self.user_cloud.get_volume(volume_id)
        self.assertIsNotNone(volume)
        self.assertEqual(volume['name'], volume['display_name'])
        self.assertEqual([], volume['attachments'])
        self._wait_for_detach(volume.id)
        self.assertTrue(self.user_cloud.delete_volume(volume_id))
        self.assertIsNone(self.user_cloud.get_server(self.server_name))
        self.assertIsNone(self.user_cloud.get_volume(volume_id))

    def test_create_boot_from_volume_preexisting_terminate(self):
        if not self.user_cloud.has_service('volume'):
            self.skipTest('volume service not supported by cloud')
        self.addCleanup(self._cleanup_servers_and_volumes, self.server_name)
        volume = self.user_cloud.create_volume(
            size=1, name=self.server_name, image=self.image, wait=True)
        server = self.user_cloud.create_server(
            name=self.server_name,
            image=None,
            flavor=self.flavor,
            boot_volume=volume,
            terminate_volume=True,
            volume_size=1,
            wait=True)
        volume_id = self._assert_volume_attach(server, volume_id=volume['id'])
        self.assertTrue(
            self.user_cloud.delete_server(self.server_name, wait=True))
        volume = self.user_cloud.get_volume(volume_id)
        # We can either get None (if the volume delete was quick), or a volume
        # that is in the process of being deleted.
        if volume:
            self.assertEqual('deleting', volume.status)
        self.assertIsNone(self.user_cloud.get_server(self.server_name))

    def test_create_image_snapshot_wait_active(self):
        self.addCleanup(self._cleanup_servers_and_volumes, self.server_name)
        server = self.user_cloud.create_server(
            name=self.server_name,
            image=self.image,
            flavor=self.flavor,
            admin_pass='sheiqu9loegahSh',
            wait=True)
        image = self.user_cloud.create_image_snapshot('test-snapshot', server,
                                                      wait=True)
        self.addCleanup(self.user_cloud.delete_image, image['id'])
        self.assertEqual('active', image['status'])

    def test_set_and_delete_metadata(self):
        self.addCleanup(self._cleanup_servers_and_volumes, self.server_name)
        self.user_cloud.create_server(
            name=self.server_name,
            image=self.image,
            flavor=self.flavor,
            wait=True)
        self.user_cloud.set_server_metadata(self.server_name,
                                            {'key1': 'value1',
                                             'key2': 'value2'})
        updated_server = self.user_cloud.get_server(self.server_name)
        self.assertEqual(set(updated_server.metadata.items()),
                         set({'key1': 'value1', 'key2': 'value2'}.items()))

        self.user_cloud.set_server_metadata(self.server_name,
                                            {'key2': 'value3'})
        updated_server = self.user_cloud.get_server(self.server_name)
        self.assertEqual(set(updated_server.metadata.items()),
                         set({'key1': 'value1', 'key2': 'value3'}.items()))

        self.user_cloud.delete_server_metadata(self.server_name, ['key2'])
        updated_server = self.user_cloud.get_server(self.server_name)
        self.assertEqual(set(updated_server.metadata.items()),
                         set({'key1': 'value1'}.items()))

        self.user_cloud.delete_server_metadata(self.server_name, ['key1'])
        updated_server = self.user_cloud.get_server(self.server_name)
        self.assertEqual(set(updated_server.metadata.items()), set([]))

        self.assertRaises(
            exc.OpenStackCloudURINotFound,
            self.user_cloud.delete_server_metadata,
            self.server_name, ['key1'])

    def test_update_server(self):
        self.addCleanup(self._cleanup_servers_and_volumes, self.server_name)
        self.user_cloud.create_server(
            name=self.server_name,
            image=self.image,
            flavor=self.flavor,
            wait=True)
        server_updated = self.user_cloud.update_server(
            self.server_name,
            name='new_name'
        )
        self.assertEqual('new_name', server_updated['name'])
