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

import datetime

from fixtures import TimeoutException

from openstack.compute.v2 import limits as _limits
from openstack import exceptions
from openstack.tests.functional import base
from openstack import utils


class TestCompute(base.BaseFunctionalTest):
    # OS_TEST_TIMEOUT is 90 sec by default but on a bad day,
    # test_attach_detach_volume can take more time.
    TIMEOUT_SCALING_FACTOR = 2

    def setUp(self):
        super().setUp()
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
        except (exceptions.ResourceTimeout, TimeoutException):
            # Ups, some timeout occurred during process of deletion server
            # or volumes, so now we will try to call delete each of them
            # once again and we will try to live with it
            self.user_cloud.delete_server(server.name)
            for volume in volumes:
                self.operator_cloud.delete_volume(
                    volume.id, wait=False, force=True
                )

    def test_create_and_delete_server(self):
        self.addCleanup(self._cleanup_servers_and_volumes, self.server_name)
        server = self.user_cloud.create_server(
            name=self.server_name,
            image=self.image,
            flavor=self.flavor,
            wait=True,
        )
        self.assertEqual(self.server_name, server['name'])
        self.assertEqual(self.image.id, server['image']['id'])
        self.assertEqual(self.flavor.name, server['flavor']['original_name'])
        self.assertIsNotNone(server['adminPass'])
        self.assertTrue(
            self.user_cloud.delete_server(self.server_name, wait=True)
        )
        srv = self.user_cloud.get_server(self.server_name)
        self.assertTrue(srv is None or srv.status.lower() == 'deleted')

    def test_create_and_delete_server_auto_ip_delete_ips(self):
        self.addCleanup(self._cleanup_servers_and_volumes, self.server_name)
        server = self.user_cloud.create_server(
            name=self.server_name,
            image=self.image,
            flavor=self.flavor,
            auto_ip=True,
            wait=True,
        )
        self.assertEqual(self.server_name, server['name'])
        self.assertEqual(self.image.id, server['image']['id'])
        self.assertEqual(self.flavor.name, server['flavor']['original_name'])
        self.assertIsNotNone(server['adminPass'])
        self.assertTrue(
            self.user_cloud.delete_server(
                self.server_name, wait=True, delete_ips=True
            )
        )
        srv = self.user_cloud.get_server(self.server_name)
        self.assertTrue(srv is None or srv.status.lower() == 'deleted')

    def test_attach_detach_volume(self):
        self.skipTest('Volume functional tests temporarily disabled')
        server_name = self.getUniqueString()
        self.addCleanup(self._cleanup_servers_and_volumes, server_name)
        server = self.user_cloud.create_server(
            name=server_name, image=self.image, flavor=self.flavor, wait=True
        )
        volume = self.user_cloud.create_volume(1)
        vol_attachment = self.user_cloud.attach_volume(server, volume)
        for key in ('device', 'serverId', 'volumeId'):
            self.assertIn(key, vol_attachment)
            self.assertTrue(vol_attachment[key])  # assert string is not empty
        self.assertIsNone(self.user_cloud.detach_volume(server, volume))

    def test_attach_volume_create_snapshot(self):
        self.skipTest('Volume functional tests temporarily disabled')
        server_name = self.getUniqueString()
        self.addCleanup(self._cleanup_servers_and_volumes, server_name)
        server = self.user_cloud.create_server(
            name=server_name, image=self.image, flavor=self.flavor, wait=True
        )
        volume = self.user_cloud.create_volume(1)
        vol_attachment = self.user_cloud.attach_volume(server, volume)
        for key in ('device', 'serverId', 'volumeId'):
            self.assertIn(key, vol_attachment)
            self.assertTrue(vol_attachment[key])  # assert string is not empty
        snapshot = self.user_cloud.create_volume_snapshot(
            volume_id=volume.id, force=True, wait=True
        )
        self.addCleanup(self.user_cloud.delete_volume_snapshot, snapshot['id'])
        self.assertIsNotNone(snapshot)

    def test_create_and_delete_server_with_config_drive(self):
        self.addCleanup(self._cleanup_servers_and_volumes, self.server_name)
        server = self.user_cloud.create_server(
            name=self.server_name,
            image=self.image,
            flavor=self.flavor,
            config_drive=True,
            wait=True,
        )
        self.assertEqual(self.server_name, server['name'])
        self.assertEqual(self.image.id, server['image']['id'])
        self.assertEqual(self.flavor.name, server['flavor']['original_name'])
        self.assertTrue(server['has_config_drive'])
        self.assertIsNotNone(server['adminPass'])
        self.assertTrue(
            self.user_cloud.delete_server(self.server_name, wait=True)
        )
        srv = self.user_cloud.get_server(self.server_name)
        self.assertTrue(srv is None or srv.status.lower() == 'deleted')

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
            wait=True,
        )
        self.assertEqual(self.server_name, server['name'])
        self.assertEqual(self.image.id, server['image']['id'])
        self.assertEqual(self.flavor.name, server['flavor']['original_name'])
        self.assertFalse(server['has_config_drive'])
        self.assertIsNotNone(server['adminPass'])
        self.assertTrue(
            self.user_cloud.delete_server(self.server_name, wait=True)
        )
        srv = self.user_cloud.get_server(self.server_name)
        self.assertTrue(srv is None or srv.status.lower() == 'deleted')

    def test_list_all_servers(self):
        if not self.operator_cloud:
            self.skipTest("Operator cloud is required for this test")
        self.addCleanup(self._cleanup_servers_and_volumes, self.server_name)
        server = self.user_cloud.create_server(
            name=self.server_name,
            image=self.image,
            flavor=self.flavor,
            wait=True,
        )
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
            exceptions.SDKException,
            self.user_cloud.list_servers,
            all_projects=True,
        )

    def test_create_server_image_flavor_dict(self):
        self.addCleanup(self._cleanup_servers_and_volumes, self.server_name)
        server = self.user_cloud.create_server(
            name=self.server_name,
            image={'id': self.image.id},
            flavor={'id': self.flavor.id},
            wait=True,
        )
        self.assertEqual(self.server_name, server['name'])
        self.assertEqual(self.image.id, server['image']['id'])
        self.assertEqual(self.flavor.name, server['flavor']['original_name'])
        self.assertIsNotNone(server['adminPass'])
        self.assertTrue(
            self.user_cloud.delete_server(self.server_name, wait=True)
        )
        srv = self.user_cloud.get_server(self.server_name)
        self.assertTrue(srv is None or srv.status.lower() == 'deleted')

    def test_get_server_console(self):
        self.addCleanup(self._cleanup_servers_and_volumes, self.server_name)
        server = self.user_cloud.create_server(
            name=self.server_name,
            image=self.image,
            flavor=self.flavor,
            wait=True,
        )
        # _get_server_console_output does not trap HTTP exceptions, so this
        # returning a string tests that the call is correct. Testing that
        # the cloud returns actual data in the output is out of scope.
        log = self.user_cloud._get_server_console_output(server_id=server.id)
        self.assertIsInstance(log, str)

    def test_get_server_console_name_or_id(self):
        self.addCleanup(self._cleanup_servers_and_volumes, self.server_name)
        self.user_cloud.create_server(
            name=self.server_name,
            image=self.image,
            flavor=self.flavor,
            wait=True,
        )
        log = self.user_cloud.get_server_console(server=self.server_name)
        self.assertIsInstance(log, str)

    def test_list_availability_zone_names(self):
        self.assertEqual(
            ['nova'], self.user_cloud.list_availability_zone_names()
        )

    def test_get_server_console_bad_server(self):
        self.assertRaises(
            exceptions.SDKException,
            self.user_cloud.get_server_console,
            server=self.server_name,
        )

    def test_create_and_delete_server_with_admin_pass(self):
        self.addCleanup(self._cleanup_servers_and_volumes, self.server_name)
        server = self.user_cloud.create_server(
            name=self.server_name,
            image=self.image,
            flavor=self.flavor,
            admin_pass='sheiqu9loegahSh',
            wait=True,
        )
        self.assertEqual(self.server_name, server['name'])
        self.assertEqual(self.image.id, server['image']['id'])
        self.assertEqual(self.flavor.name, server['flavor']['original_name'])
        self.assertEqual(server['adminPass'], 'sheiqu9loegahSh')
        self.assertTrue(
            self.user_cloud.delete_server(self.server_name, wait=True)
        )
        srv = self.user_cloud.get_server(self.server_name)
        self.assertTrue(srv is None or srv.status.lower() == 'deleted')

    def test_get_image_id(self):
        self.assertEqual(
            self.image.id, self.user_cloud.get_image_id(self.image.id)
        )
        self.assertEqual(
            self.image.id, self.user_cloud.get_image_id(self.image.name)
        )

    def test_get_image_name(self):
        self.assertEqual(
            self.image.name, self.user_cloud.get_image_name(self.image.id)
        )
        self.assertEqual(
            self.image.name, self.user_cloud.get_image_name(self.image.name)
        )

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
        self.assertEqual(1, len(volume['attachments']))
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
            wait=True,
        )
        volume_id = self._assert_volume_attach(server)
        volume = self.user_cloud.get_volume(volume_id)
        self.assertIsNotNone(volume)
        self.assertEqual(volume['name'], volume['display_name'])
        self.assertTrue(volume['bootable'])
        self.assertEqual(server['id'], volume['attachments'][0]['server_id'])
        self.assertTrue(self.user_cloud.delete_server(server.id, wait=True))
        self._wait_for_detach(volume.id)
        self.assertTrue(self.user_cloud.delete_volume(volume.id, wait=True))
        srv = self.user_cloud.get_server(self.server_name)
        self.assertTrue(srv is None or srv.status.lower() == 'deleted')
        self.assertIsNone(self.user_cloud.get_volume(volume.id))

    def _wait_for_detach(self, volume_id):
        # Volumes do not show up as unattached for a bit immediately after
        # deleting a server that had had a volume attached. Yay for eventual
        # consistency!
        for count in utils.iterate_timeout(
            60,
            f'Timeout waiting for volume {volume_id} to detach',
        ):
            volume = self.user_cloud.get_volume(volume_id)
            assert volume is not None
            if volume.status in (
                'available',
                'error',
                'error_restoring',
                'error_extending',
            ):
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
            wait=True,
        )
        volume_id = self._assert_volume_attach(server)
        self.assertTrue(
            self.user_cloud.delete_server(self.server_name, wait=True)
        )
        volume = self.user_cloud.get_volume(volume_id)
        # We can either get None (if the volume delete was quick), or a volume
        # that is in the process of being deleted.
        if volume:
            self.assertEqual('deleting', volume.status)
        srv = self.user_cloud.get_server(self.server_name)
        self.assertTrue(srv is None or srv.status.lower() == 'deleted')

    def test_create_boot_from_volume_preexisting(self):
        self.skipTest('Volume functional tests temporarily disabled')
        if not self.user_cloud.has_service('volume'):
            self.skipTest('volume service not supported by cloud')
        self.addCleanup(self._cleanup_servers_and_volumes, self.server_name)
        volume = self.user_cloud.create_volume(
            size=1, name=self.server_name, image=self.image, wait=True
        )
        self.addCleanup(self.user_cloud.delete_volume, volume.id)
        server = self.user_cloud.create_server(
            name=self.server_name,
            image=None,
            flavor=self.flavor,
            boot_volume=volume,
            volume_size=1,
            wait=True,
        )
        volume_id = self._assert_volume_attach(server, volume_id=volume['id'])
        self.assertTrue(
            self.user_cloud.delete_server(self.server_name, wait=True)
        )
        volume = self.user_cloud.get_volume(volume_id)
        self.assertIsNotNone(volume)
        self.assertEqual(volume['name'], volume['display_name'])
        self.assertTrue(volume['bootable'])
        self.assertEqual([], volume['attachments'])
        self._wait_for_detach(volume.id)
        self.assertTrue(self.user_cloud.delete_volume(volume_id))
        srv = self.user_cloud.get_server(self.server_name)
        self.assertTrue(srv is None or srv.status.lower() == 'deleted')
        self.assertIsNone(self.user_cloud.get_volume(volume_id))

    def test_create_boot_attach_volume(self):
        self.skipTest('Volume functional tests temporarily disabled')
        if not self.user_cloud.has_service('volume'):
            self.skipTest('volume service not supported by cloud')
        self.addCleanup(self._cleanup_servers_and_volumes, self.server_name)
        volume = self.user_cloud.create_volume(
            size=1, name=self.server_name, image=self.image, wait=True
        )
        self.addCleanup(self.user_cloud.delete_volume, volume['id'])
        server = self.user_cloud.create_server(
            name=self.server_name,
            flavor=self.flavor,
            image=self.image,
            boot_from_volume=False,
            volumes=[volume],
            wait=True,
        )
        volume_id = self._assert_volume_attach(
            server, volume_id=volume['id'], image={'id': self.image['id']}
        )
        self.assertTrue(
            self.user_cloud.delete_server(self.server_name, wait=True)
        )
        volume = self.user_cloud.get_volume(volume_id)
        self.assertIsNotNone(volume)
        self.assertEqual(volume['name'], volume['display_name'])
        self.assertEqual([], volume['attachments'])
        self._wait_for_detach(volume.id)
        self.assertTrue(self.user_cloud.delete_volume(volume_id))
        srv = self.user_cloud.get_server(self.server_name)
        self.assertTrue(srv is None or srv.status.lower() == 'deleted')
        self.assertIsNone(self.user_cloud.get_volume(volume_id))

    def test_create_boot_from_volume_preexisting_terminate(self):
        self.skipTest('Volume functional tests temporarily disabled')
        if not self.user_cloud.has_service('volume'):
            self.skipTest('volume service not supported by cloud')
        self.addCleanup(self._cleanup_servers_and_volumes, self.server_name)
        volume = self.user_cloud.create_volume(
            size=1, name=self.server_name, image=self.image, wait=True
        )
        server = self.user_cloud.create_server(
            name=self.server_name,
            image=None,
            flavor=self.flavor,
            boot_volume=volume,
            terminate_volume=True,
            volume_size=1,
            wait=True,
        )
        volume_id = self._assert_volume_attach(server, volume_id=volume['id'])
        self.assertTrue(
            self.user_cloud.delete_server(self.server_name, wait=True)
        )
        volume = self.user_cloud.get_volume(volume_id)
        # We can either get None (if the volume delete was quick), or a volume
        # that is in the process of being deleted.
        if volume:
            self.assertEqual('deleting', volume.status)
        srv = self.user_cloud.get_server(self.server_name)
        self.assertTrue(srv is None or srv.status.lower() == 'deleted')

    def test_create_image_snapshot_wait_active(self):
        self.addCleanup(self._cleanup_servers_and_volumes, self.server_name)
        server = self.user_cloud.create_server(
            name=self.server_name,
            image=self.image,
            flavor=self.flavor,
            admin_pass='sheiqu9loegahSh',
            wait=True,
        )
        image = self.user_cloud.create_image_snapshot(
            'test-snapshot', server, wait=True
        )
        self.addCleanup(self.user_cloud.delete_image, image['id'])
        self.assertEqual('active', image['status'])

    def test_set_and_delete_metadata(self):
        self.addCleanup(self._cleanup_servers_and_volumes, self.server_name)
        self.user_cloud.create_server(
            name=self.server_name,
            image=self.image,
            flavor=self.flavor,
            wait=True,
        )
        self.user_cloud.set_server_metadata(
            self.server_name, {'key1': 'value1', 'key2': 'value2'}
        )
        updated_server = self.user_cloud.get_server(self.server_name)
        assert updated_server is not None
        self.assertEqual(
            set(updated_server.metadata.items()),
            set({'key1': 'value1', 'key2': 'value2'}.items()),
        )

        self.user_cloud.set_server_metadata(
            self.server_name, {'key2': 'value3'}
        )
        updated_server = self.user_cloud.get_server(self.server_name)
        assert updated_server is not None
        self.assertEqual(
            set(updated_server.metadata.items()),
            set({'key1': 'value1', 'key2': 'value3'}.items()),
        )

        self.user_cloud.delete_server_metadata(self.server_name, ['key2'])
        updated_server = self.user_cloud.get_server(self.server_name)
        assert updated_server is not None
        self.assertEqual(
            set(updated_server.metadata.items()),
            set({'key1': 'value1'}.items()),
        )

        self.user_cloud.delete_server_metadata(self.server_name, ['key1'])
        updated_server = self.user_cloud.get_server(self.server_name)
        assert updated_server is not None
        self.assertEqual(set(updated_server.metadata.items()), set())

        self.assertRaises(
            exceptions.NotFoundException,
            self.user_cloud.delete_server_metadata,
            self.server_name,
            ['key1'],
        )

    def test_update_server(self):
        self.addCleanup(self._cleanup_servers_and_volumes, self.server_name)
        self.user_cloud.create_server(
            name=self.server_name,
            image=self.image,
            flavor=self.flavor,
            wait=True,
        )
        server_updated = self.user_cloud.update_server(
            self.server_name, name='new_name'
        )
        assert server_updated is not None
        self.assertEqual('new_name', server_updated['name'])

    def test_get_compute_usage(self):
        '''Test usage functionality'''
        # Add a server so that we can know we have usage
        if not self.operator_cloud:
            # TODO(gtema) rework method not to require getting project
            self.skipTest("Operator cloud is required for this test")
        self.addCleanup(self._cleanup_servers_and_volumes, self.server_name)
        self.user_cloud.create_server(
            name=self.server_name,
            image=self.image,
            flavor=self.flavor,
            wait=True,
        )
        start = datetime.datetime.now() - datetime.timedelta(seconds=5)
        usage = self.operator_cloud.get_compute_usage('demo', start)
        self.add_info_on_exception('usage', usage)
        self.assertIsNotNone(usage)
        self.assertIn('total_hours', usage)
        self.assertIn('start', usage)
        self.assertEqual(start.isoformat(), usage['start'])
        self.assertIn('location', usage)


class TestAggregate(base.BaseFunctionalTest):
    def test_aggregates(self):
        if not self.operator_cloud:
            self.skipTest("Operator cloud is required for this test")
        aggregate_name = self.getUniqueString()
        availability_zone = self.getUniqueString()
        self.addCleanup(self.cleanup, aggregate_name)
        aggregate = self.operator_cloud.create_aggregate(aggregate_name)

        aggregate_ids = [
            v['id'] for v in self.operator_cloud.list_aggregates()
        ]
        self.assertIn(aggregate['id'], aggregate_ids)

        aggregate = self.operator_cloud.update_aggregate(
            aggregate_name, availability_zone=availability_zone
        )
        self.assertEqual(availability_zone, aggregate['availability_zone'])

        aggregate = self.operator_cloud.set_aggregate_metadata(
            aggregate_name, {'key': 'value'}
        )
        self.assertIn('key', aggregate['metadata'])

        aggregate = self.operator_cloud.set_aggregate_metadata(
            aggregate_name, {'key': None}
        )
        self.assertNotIn('key', aggregate['metadata'])

        # Validate that we can delete by name
        self.assertTrue(self.operator_cloud.delete_aggregate(aggregate_name))

    def cleanup(self, aggregate_name):
        aggregate = self.operator_cloud.get_aggregate(aggregate_name)
        if aggregate:
            self.operator_cloud.delete_aggregate(aggregate['id'])


class TestFlavor(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()

        # Generate a random name for flavors in this test
        self.new_item_name = self.getUniqueString('flavor')

        self.addCleanup(self._cleanup_flavors)

    def _cleanup_flavors(self):
        exception_list = list()
        if self.operator_cloud:
            for f in self.operator_cloud.list_flavors(get_extra=False):
                if f['name'].startswith(self.new_item_name):
                    try:
                        self.operator_cloud.delete_flavor(f['id'])
                    except Exception as e:
                        # We were unable to delete a flavor, let's try with
                        # next
                        exception_list.append(str(e))
                    continue
        if exception_list:
            # Raise an error: we must make users aware that something went
            # wrong
            raise exceptions.SDKException('\n'.join(exception_list))

    def test_create_flavor(self):
        if not self.operator_cloud:
            self.skipTest("Operator cloud is required for this test")

        flavor_name = self.new_item_name + '_create'
        flavor_kwargs = dict(
            name=flavor_name,
            ram=1024,
            vcpus=2,
            disk=10,
            ephemeral=5,
            swap=100,
            rxtx_factor=1.5,
            is_public=True,
        )

        flavor = self.operator_cloud.create_flavor(**flavor_kwargs)

        self.assertIsNotNone(flavor['id'])

        # When properly normalized, we should always get an extra_specs
        # and expect empty dict on create.
        self.assertIn('extra_specs', flavor)
        self.assertEqual({}, flavor['extra_specs'])

        # We should also always have ephemeral and public attributes
        self.assertIn('ephemeral', flavor)
        self.assertEqual(5, flavor['ephemeral'])
        self.assertIn('is_public', flavor)
        self.assertTrue(flavor['is_public'])

        for key in flavor_kwargs.keys():
            self.assertIn(key, flavor)
        for key, value in flavor_kwargs.items():
            self.assertEqual(value, flavor[key])

    def test_list_flavors(self):
        pub_flavor_name = self.new_item_name + '_public'
        priv_flavor_name = self.new_item_name + '_private'
        public_kwargs = dict(
            name=pub_flavor_name, ram=1024, vcpus=2, disk=10, is_public=True
        )
        private_kwargs = dict(
            name=priv_flavor_name, ram=1024, vcpus=2, disk=10, is_public=False
        )

        if self.operator_cloud:
            # Create a public and private flavor. We expect both to be listed
            # for an operator.
            self.operator_cloud.create_flavor(**public_kwargs)
            self.operator_cloud.create_flavor(**private_kwargs)

            flavors = self.operator_cloud.list_flavors(get_extra=False)

            # Flavor list will include the standard devstack flavors. We just
            # want to make sure both of the flavors we just created are
            # present.
            found = []
            for f in flavors:
                # extra_specs should be added within list_flavors()
                self.assertIn('extra_specs', f)
                if f['name'] in (pub_flavor_name, priv_flavor_name):
                    found.append(f)
            self.assertEqual(2, len(found))
        else:
            self.user_cloud.list_flavors()

    def test_flavor_access(self):
        if not self.operator_cloud:
            self.skipTest("Operator cloud is required for this test")

        priv_flavor_name = self.new_item_name + '_private'
        private_kwargs = dict(
            name=priv_flavor_name, ram=1024, vcpus=2, disk=10, is_public=False
        )
        new_flavor = self.operator_cloud.create_flavor(**private_kwargs)

        # Validate the 'demo' user cannot see the new flavor
        flavors = self.user_cloud.search_flavors(priv_flavor_name)
        self.assertEqual(0, len(flavors))

        # We need the tenant ID for the 'demo' user
        project = self.operator_cloud.get_project('demo')
        self.assertIsNotNone(project)
        assert project is not None

        # Now give 'demo' access
        self.operator_cloud.add_flavor_access(new_flavor['id'], project['id'])

        # Now see if the 'demo' user has access to it
        flavors = self.user_cloud.search_flavors(priv_flavor_name)
        self.assertEqual(1, len(flavors))
        self.assertEqual(priv_flavor_name, flavors[0]['name'])

        # Now see if the 'demo' user has access to it without needing
        #  the demo_cloud access.
        acls = self.operator_cloud.list_flavor_access(new_flavor['id'])
        self.assertEqual(1, len(acls))
        self.assertEqual(project['id'], acls[0]['tenant_id'])

        # Now revoke the access and make sure we can't find it
        self.operator_cloud.remove_flavor_access(
            new_flavor['id'], project['id']
        )
        flavors = self.user_cloud.search_flavors(priv_flavor_name)
        self.assertEqual(0, len(flavors))

    def test_set_unset_flavor_specs(self):
        """
        Test setting and unsetting flavor extra specs
        """
        if not self.operator_cloud:
            self.skipTest("Operator cloud is required for this test")

        flavor_name = self.new_item_name + '_spec_test'
        kwargs = dict(name=flavor_name, ram=1024, vcpus=2, disk=10)
        new_flavor = self.operator_cloud.create_flavor(**kwargs)

        # Expect no extra_specs
        self.assertEqual({}, new_flavor['extra_specs'])

        # Now set them
        extra_specs = {'foo': 'aaa', 'bar': 'bbb'}
        self.operator_cloud.set_flavor_specs(new_flavor['id'], extra_specs)
        mod_flavor = self.operator_cloud.get_flavor(
            new_flavor['id'], get_extra=True
        )
        assert mod_flavor is not None

        # Verify extra_specs were set
        self.assertIn('extra_specs', mod_flavor)
        self.assertEqual(extra_specs, mod_flavor['extra_specs'])

        # Unset the 'foo' value
        self.operator_cloud.unset_flavor_specs(mod_flavor['id'], ['foo'])
        mod_flavor = self.operator_cloud.get_flavor_by_id(
            new_flavor['id'], get_extra=True
        )

        # Verify 'foo' is unset and 'bar' is still set
        self.assertEqual({'bar': 'bbb'}, mod_flavor['extra_specs'])


FAKE_PUBLIC_KEY = (
    "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCkF3MX59OrlBs3dH5CU7lNmvpbrgZxSpyGj"
    "lnE8Flkirnc/Up22lpjznoxqeoTAwTW034k7Dz6aYIrZGmQwe2TkE084yqvlj45Dkyoj95fW/"
    "sZacm0cZNuL69EObEGHdprfGJQajrpz22NQoCD8TFB8Wv+8om9NH9Le6s+WPe98WC77KLw8qg"
    "fQsbIey+JawPWl4O67ZdL5xrypuRjfIPWjgy/VH85IXg/Z/GONZ2nxHgSShMkwqSFECAC5L3P"
    "HB+0+/12M/iikdatFSVGjpuHvkLOs3oe7m6HlOfluSJ85BzLWBbvva93qkGmLg4ZAc8rPh2O+"
    "YIsBUHNLLMM/oQp Generated-by-Nova\n"
)


class TestKeypairs(base.BaseFunctionalTest):
    def test_create_and_delete(self):
        '''Test creating and deleting keypairs functionality'''
        name = self.getUniqueString('keypair')
        self.addCleanup(self.user_cloud.delete_keypair, name)
        keypair = self.user_cloud.create_keypair(name=name)
        self.assertEqual(keypair['name'], name)
        self.assertIsNotNone(keypair['public_key'])
        self.assertIsNotNone(keypair['private_key'])
        self.assertIsNotNone(keypair['fingerprint'])
        self.assertEqual(keypair['type'], 'ssh')

        keypairs = self.user_cloud.list_keypairs()
        self.assertIn(name, [k['name'] for k in keypairs])

        self.user_cloud.delete_keypair(name)

        keypairs = self.user_cloud.list_keypairs()
        self.assertNotIn(name, [k['name'] for k in keypairs])

    def test_create_and_delete_with_key(self):
        '''Test creating and deleting keypairs functionality'''
        name = self.getUniqueString('keypair')
        self.addCleanup(self.user_cloud.delete_keypair, name)
        keypair = self.user_cloud.create_keypair(
            name=name, public_key=FAKE_PUBLIC_KEY
        )
        self.assertEqual(keypair['name'], name)
        self.assertIsNotNone(keypair['public_key'])
        self.assertIsNone(keypair['private_key'])
        self.assertIsNotNone(keypair['fingerprint'])
        self.assertEqual(keypair['type'], 'ssh')

        keypairs = self.user_cloud.list_keypairs()
        self.assertIn(name, [k['name'] for k in keypairs])

        self.user_cloud.delete_keypair(name)

        keypairs = self.user_cloud.list_keypairs()
        self.assertNotIn(name, [k['name'] for k in keypairs])


class TestServerGroup(base.BaseFunctionalTest):
    def test_server_group(self):
        server_group_name = self.getUniqueString()
        self.addCleanup(self.cleanup, server_group_name)
        server_group = self.user_cloud.create_server_group(
            server_group_name, ['affinity']
        )

        server_group_ids = [
            v['id'] for v in self.user_cloud.list_server_groups()
        ]
        self.assertIn(server_group['id'], server_group_ids)

        self.user_cloud.delete_server_group(server_group_name)

    def cleanup(self, server_group_name):
        server_group = self.user_cloud.get_server_group(server_group_name)
        if server_group:
            self.user_cloud.delete_server_group(server_group['id'])


class TestComputeLimits(base.BaseFunctionalTest):
    def test_get_our_compute_limits(self):
        """Test limits functionality"""
        limits = self.user_cloud.get_compute_limits()
        self.assertIsNotNone(limits)

        self.assertIsInstance(limits, _limits.AbsoluteLimits)
        self.assertIsNotNone(limits.server_meta)
        self.assertIsNotNone(limits.image_meta)

    def test_get_other_compute_limits(self):
        """Test limits functionality"""
        if not self.operator_cloud:
            self.skipTest("Operator cloud is required for this test")

        limits = self.operator_cloud.get_compute_limits('demo')
        self.assertIsNotNone(limits)
        self.assertTrue(hasattr(limits, 'server_meta'))

        # Test normalize limits
        self.assertFalse(hasattr(limits, 'maxImageMeta'))


class TestComputeQuotas(base.BaseFunctionalTest):
    def test_get_quotas(self):
        '''Test quotas functionality'''
        project_id = self.user_cloud.current_project_id
        assert project_id is not None
        self.user_cloud.get_compute_quotas(project_id)

    def test_set_quotas(self):
        '''Test quotas functionality'''
        if not self.operator_cloud:
            self.skipTest("Operator cloud is required for this test")

        quotas = self.operator_cloud.get_compute_quotas('demo')
        cores = quotas['cores']
        self.operator_cloud.set_compute_quotas('demo', cores=cores + 1)
        self.assertEqual(
            cores + 1, self.operator_cloud.get_compute_quotas('demo')['cores']
        )
        self.operator_cloud.delete_compute_quotas('demo')
        self.assertEqual(
            cores, self.operator_cloud.get_compute_quotas('demo')['cores']
        )


class TestRangeSearch(base.BaseFunctionalTest):
    def _filter_m1_flavors(self, results):
        """The m1 flavors are the original devstack flavors"""
        new_results = []
        for flavor in results:
            if flavor['name'].startswith("m1."):
                new_results.append(flavor)
        return new_results

    def test_range_search_bad_range(self):
        flavors = self.user_cloud.list_flavors(get_extra=False)
        self.assertRaises(
            exceptions.SDKException,
            self.user_cloud.range_search,
            flavors,
            {"ram": "<1a0"},
        )

    def test_range_search_exact(self):
        flavors = self.user_cloud.list_flavors(get_extra=False)
        result = self.user_cloud.range_search(flavors, {"ram": "4096"})
        self.assertIsInstance(result, list)
        # should only be 1 m1 flavor with 4096 ram
        result = self._filter_m1_flavors(result)
        self.assertEqual(1, len(result))
        self.assertEqual("m1.medium", result[0]['name'])

    def test_range_search_min(self):
        flavors = self.user_cloud.list_flavors(get_extra=False)
        result = self.user_cloud.range_search(flavors, {"ram": "MIN"})
        self.assertIsInstance(result, list)
        self.assertEqual(1, len(result))
        # older devstack does not have cirros256
        self.assertIn(result[0]['name'], ('cirros256', 'm1.tiny'))

    def test_range_search_max(self):
        flavors = self.user_cloud.list_flavors(get_extra=False)
        result = self.user_cloud.range_search(flavors, {"ram": "MAX"})
        self.assertIsInstance(result, list)
        self.assertEqual(1, len(result))
        self.assertEqual("m1.xlarge", result[0]['name'])

    def test_range_search_lt(self):
        flavors = self.user_cloud.list_flavors(get_extra=False)
        result = self.user_cloud.range_search(flavors, {"ram": "<1024"})
        self.assertIsInstance(result, list)
        # should only be 1 m1 flavor with <1024 ram
        result = self._filter_m1_flavors(result)
        self.assertEqual(1, len(result))
        self.assertEqual("m1.tiny", result[0]['name'])

    def test_range_search_gt(self):
        flavors = self.user_cloud.list_flavors(get_extra=False)
        result = self.user_cloud.range_search(flavors, {"ram": ">4096"})
        self.assertIsInstance(result, list)
        # should only be 2 m1 flavors with >4096 ram
        result = self._filter_m1_flavors(result)
        self.assertEqual(2, len(result))
        flavor_names = [r['name'] for r in result]
        self.assertIn("m1.large", flavor_names)
        self.assertIn("m1.xlarge", flavor_names)

    def test_range_search_le(self):
        flavors = self.user_cloud.list_flavors(get_extra=False)
        result = self.user_cloud.range_search(flavors, {"ram": "<=4096"})
        self.assertIsInstance(result, list)
        # should only be 3 m1 flavors with <=4096 ram
        result = self._filter_m1_flavors(result)
        self.assertEqual(3, len(result))
        flavor_names = [r['name'] for r in result]
        self.assertIn("m1.tiny", flavor_names)
        self.assertIn("m1.small", flavor_names)
        self.assertIn("m1.medium", flavor_names)

    def test_range_search_ge(self):
        flavors = self.user_cloud.list_flavors(get_extra=False)
        result = self.user_cloud.range_search(flavors, {"ram": ">=4096"})
        self.assertIsInstance(result, list)
        # should only be 3 m1 flavors with >=4096 ram
        result = self._filter_m1_flavors(result)
        self.assertEqual(3, len(result))
        flavor_names = [r['name'] for r in result]
        self.assertIn("m1.medium", flavor_names)
        self.assertIn("m1.large", flavor_names)
        self.assertIn("m1.xlarge", flavor_names)

    def test_range_search_multi_1(self):
        flavors = self.user_cloud.list_flavors(get_extra=False)
        result = self.user_cloud.range_search(
            flavors, {"ram": "MIN", "vcpus": "MIN"}
        )
        self.assertIsInstance(result, list)
        self.assertEqual(1, len(result))
        # older devstack does not have cirros256
        self.assertIn(result[0]['name'], ('cirros256', 'm1.tiny'))

    def test_range_search_multi_2(self):
        flavors = self.user_cloud.list_flavors(get_extra=False)
        result = self.user_cloud.range_search(
            flavors, {"ram": "<1024", "vcpus": "MIN"}
        )
        self.assertIsInstance(result, list)
        result = self._filter_m1_flavors(result)
        self.assertEqual(1, len(result))
        flavor_names = [r['name'] for r in result]
        self.assertIn("m1.tiny", flavor_names)

    def test_range_search_multi_3(self):
        flavors = self.user_cloud.list_flavors(get_extra=False)
        result = self.user_cloud.range_search(
            flavors, {"ram": ">=4096", "vcpus": "<6"}
        )
        self.assertIsInstance(result, list)
        result = self._filter_m1_flavors(result)
        self.assertEqual(2, len(result))
        flavor_names = [r['name'] for r in result]
        self.assertIn("m1.medium", flavor_names)
        self.assertIn("m1.large", flavor_names)

    def test_range_search_multi_4(self):
        flavors = self.user_cloud.list_flavors(get_extra=False)
        result = self.user_cloud.range_search(
            flavors, {"ram": ">=4096", "vcpus": "MAX"}
        )
        self.assertIsInstance(result, list)
        self.assertEqual(1, len(result))
        # This is the only result that should have max vcpu
        self.assertEqual("m1.xlarge", result[0]['name'])
