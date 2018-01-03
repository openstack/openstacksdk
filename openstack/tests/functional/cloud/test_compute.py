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

import datetime

from fixtures import TimeoutException
import six

from openstack.cloud import exc
from openstack.tests.functional.cloud import base
from openstack.tests.functional.cloud.util import pick_flavor
from openstack import utils


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
        try:
            self.user_cloud.delete_server(server.name, wait=True)
            for volume in volumes:
                if volume.status != 'deleting':
                    self.user_cloud.delete_volume(volume.id, wait=True)
        except (exc.OpenStackCloudTimeout, TimeoutException):
            # Ups, some timeout occured during process of deletion server
            # or volumes, so now we will try to call delete each of them
            # once again and we will try to live with it
            self.user_cloud.delete_server(server.name)
            for volume in volumes:
                self.operator_cloud.delete_volume(
                    volume.id, wait=False, force=True)

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

    def test_create_and_delete_server_auto_ip_delete_ips(self):
        self.addCleanup(self._cleanup_servers_and_volumes, self.server_name)
        server = self.user_cloud.create_server(
            name=self.server_name,
            image=self.image,
            flavor=self.flavor,
            auto_ip=True,
            wait=True)
        self.assertEqual(self.server_name, server['name'])
        self.assertEqual(self.image.id, server['image']['id'])
        self.assertEqual(self.flavor.id, server['flavor']['id'])
        self.assertIsNotNone(server['adminPass'])
        self.assertTrue(
            self.user_cloud.delete_server(
                self.server_name, wait=True, delete_ips=True))
        self.assertIsNone(self.user_cloud.get_server(self.server_name))

    def test_attach_detach_volume(self):
        self.skipTest('Volume functional tests temporarily disabled')
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

    def test_create_and_delete_server_with_config_drive(self):
        self.addCleanup(self._cleanup_servers_and_volumes, self.server_name)
        server = self.user_cloud.create_server(
            name=self.server_name,
            image=self.image,
            flavor=self.flavor,
            config_drive=True,
            wait=True)
        self.assertEqual(self.server_name, server['name'])
        self.assertEqual(self.image.id, server['image']['id'])
        self.assertEqual(self.flavor.id, server['flavor']['id'])
        self.assertTrue(server['has_config_drive'])
        self.assertIsNotNone(server['adminPass'])
        self.assertTrue(
            self.user_cloud.delete_server(self.server_name, wait=True))
        self.assertIsNone(self.user_cloud.get_server(self.server_name))

    def test_create_and_delete_server_with_config_drive_none(self):
        # check that we're not sending invalid values for config_drive
        # if it's passed in explicitly as None - which nodepool does if it's
        # not set in the config
        self.addCleanup(self._cleanup_servers_and_volumes, self.server_name)
        server = self.user_cloud.create_server(
            name=self.server_name,
            image=self.image,
            flavor=self.flavor,
            config_drive=None,
            wait=True)
        self.assertEqual(self.server_name, server['name'])
        self.assertEqual(self.image.id, server['image']['id'])
        self.assertEqual(self.flavor.id, server['flavor']['id'])
        self.assertFalse(server['has_config_drive'])
        self.assertIsNotNone(server['adminPass'])
        self.assertTrue(
            self.user_cloud.delete_server(
                self.server_name, wait=True))
        self.assertIsNone(self.user_cloud.get_server(self.server_name))

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
        # _get_server_console_output does not trap HTTP exceptions, so this
        # returning a string tests that the call is correct. Testing that
        # the cloud returns actual data in the output is out of scope.
        log = self.user_cloud._get_server_console_output(server_id=server.id)
        self.assertTrue(isinstance(log, six.string_types))

    def test_get_server_console_name_or_id(self):
        self.addCleanup(self._cleanup_servers_and_volumes, self.server_name)
        self.user_cloud.create_server(
            name=self.server_name,
            image=self.image,
            flavor=self.flavor,
            wait=True)
        log = self.user_cloud.get_server_console(server=self.server_name)
        self.assertTrue(isinstance(log, six.string_types))

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
        self.skipTest('Volume functional tests temporarily disabled')
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
        self.assertTrue(volume['bootable'])
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
        for count in utils.iterate_timeout(
                60,
                'Timeout waiting for volume {volume_id} to detach'.format(
                    volume_id=volume_id)):
            volume = self.user_cloud.get_volume(volume_id)
            if volume.status in (
                    'available', 'error',
                    'error_restoring', 'error_extending'):
                return

    def test_create_terminate_volume_image(self):
        self.skipTest('Volume functional tests temporarily disabled')
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
        self.skipTest('Volume functional tests temporarily disabled')
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
        self.assertTrue(volume['bootable'])
        self.assertEqual([], volume['attachments'])
        self._wait_for_detach(volume.id)
        self.assertTrue(self.user_cloud.delete_volume(volume_id))
        self.assertIsNone(self.user_cloud.get_server(self.server_name))
        self.assertIsNone(self.user_cloud.get_volume(volume_id))

    def test_create_boot_attach_volume(self):
        self.skipTest('Volume functional tests temporarily disabled')
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
        self.skipTest('Volume functional tests temporarily disabled')
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

    def test_get_compute_usage(self):
        '''Test usage functionality'''
        # Add a server so that we can know we have usage
        self.addCleanup(self._cleanup_servers_and_volumes, self.server_name)
        self.user_cloud.create_server(
            name=self.server_name,
            image=self.image,
            flavor=self.flavor,
            wait=True)
        start = datetime.datetime.now() - datetime.timedelta(seconds=5)
        usage = self.operator_cloud.get_compute_usage('demo', start)
        self.add_info_on_exception('usage', usage)
        self.assertIsNotNone(usage)
        self.assertIn('total_hours', usage)
        self.assertIn('started_at', usage)
        self.assertEqual(start.isoformat(), usage['started_at'])
        self.assertIn('location', usage)
