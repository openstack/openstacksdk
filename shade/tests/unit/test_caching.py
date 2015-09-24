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
import tempfile

import mock
import os_client_config as occ
import testtools
import yaml

import shade
from shade import exc
from shade import meta
from shade.tests import fakes
from shade.tests.unit import base


class TestMemoryCache(base.TestCase):

    CACHING_CONFIG = {
        'cache':
        {
            'max_age': 90,
            'class': 'dogpile.cache.memory',
        },
        'clouds':
        {
            '_cache_test_':
            {
                'auth':
                {
                    'auth_url': 'http://198.51.100.1:35357/v2.0',
                    'username': '_test_user_',
                    'password': '_test_pass_',
                    'project_name': '_test_project_',
                },
                'region_name': '_test_region_',
            },
        },
    }

    def setUp(self):
        super(TestMemoryCache, self).setUp()

        # Isolate os-client-config from test environment
        config = tempfile.NamedTemporaryFile(delete=False)
        config.write(bytes(yaml.dump(self.CACHING_CONFIG).encode('utf-8')))
        config.close()
        vendor = tempfile.NamedTemporaryFile(delete=False)
        vendor.write(b'{}')
        vendor.close()

        self.cloud_config = occ.OpenStackConfig(config_files=[config.name],
                                                vendor_files=[vendor.name])
        self.cloud = shade.openstack_cloud(cloud='_cache_test_',
                                           config=self.cloud_config)

    def test_openstack_cloud(self):
        self.assertIsInstance(self.cloud, shade.OpenStackCloud)

    @mock.patch('shade.OpenStackCloud.keystone_client')
    def test_project_cache(self, keystone_mock):
        project = fakes.FakeProject('project_a')
        keystone_mock.projects.list.return_value = [project]
        self.assertEqual({'project_a': project}, self.cloud.project_cache)
        project_b = fakes.FakeProject('project_b')
        keystone_mock.projects.list.return_value = [project,
                                                    project_b]
        self.assertEqual(
            {'project_a': project}, self.cloud.project_cache)
        self.cloud.get_project_cache.invalidate(self.cloud)
        self.assertEqual(
            {'project_a': project,
             'project_b': project_b}, self.cloud.project_cache)

    @mock.patch('shade.OpenStackCloud.cinder_client')
    def test_list_volumes(self, cinder_mock):
        fake_volume = fakes.FakeVolume('volume1', 'available',
                                       'Volume 1 Display Name')
        fake_volume_dict = meta.obj_to_dict(fake_volume)
        cinder_mock.volumes.list.return_value = [fake_volume]
        self.assertEqual([fake_volume_dict], self.cloud.list_volumes())
        fake_volume2 = fakes.FakeVolume('volume2', 'available',
                                        'Volume 2 Display Name')
        fake_volume2_dict = meta.obj_to_dict(fake_volume2)
        cinder_mock.volumes.list.return_value = [fake_volume, fake_volume2]
        self.assertEqual([fake_volume_dict], self.cloud.list_volumes())
        self.cloud.list_volumes.invalidate(self.cloud)
        self.assertEqual([fake_volume_dict, fake_volume2_dict],
                         self.cloud.list_volumes())

    @mock.patch('shade.OpenStackCloud.cinder_client')
    def test_list_volumes_creating_invalidates(self, cinder_mock):
        fake_volume = fakes.FakeVolume('volume1', 'creating',
                                       'Volume 1 Display Name')
        fake_volume_dict = meta.obj_to_dict(fake_volume)
        cinder_mock.volumes.list.return_value = [fake_volume]
        self.assertEqual([fake_volume_dict], self.cloud.list_volumes())
        fake_volume2 = fakes.FakeVolume('volume2', 'available',
                                        'Volume 2 Display Name')
        fake_volume2_dict = meta.obj_to_dict(fake_volume2)
        cinder_mock.volumes.list.return_value = [fake_volume, fake_volume2]
        self.assertEqual([fake_volume_dict, fake_volume2_dict],
                         self.cloud.list_volumes())

    @mock.patch.object(shade.OpenStackCloud, 'cinder_client')
    def test_create_volume_invalidates(self, cinder_mock):
        fake_volb4 = fakes.FakeVolume('volume1', 'available',
                                      'Volume 1 Display Name')
        fake_volb4_dict = meta.obj_to_dict(fake_volb4)
        cinder_mock.volumes.list.return_value = [fake_volb4]
        self.assertEqual([fake_volb4_dict], self.cloud.list_volumes())
        volume = dict(display_name='junk_vol',
                      size=1,
                      display_description='test junk volume')
        fake_vol = fakes.FakeVolume('12345', 'creating', '')
        fake_vol_dict = meta.obj_to_dict(fake_vol)
        cinder_mock.volumes.create.return_value = fake_vol
        cinder_mock.volumes.list.return_value = [fake_volb4, fake_vol]

        def creating_available():
            def now_available():
                fake_vol.status = 'available'
                fake_vol_dict['status'] = 'available'
                return mock.DEFAULT
            cinder_mock.volumes.list.side_effect = now_available
            return mock.DEFAULT
        cinder_mock.volumes.list.side_effect = creating_available
        self.cloud.create_volume(wait=True, timeout=None, **volume)
        self.assertTrue(cinder_mock.volumes.create.called)
        self.assertEqual(3, cinder_mock.volumes.list.call_count)
        # If cache was not invalidated, we would not see our own volume here
        # because the first volume was available and thus would already be
        # cached.
        self.assertEqual([fake_volb4_dict, fake_vol_dict],
                         self.cloud.list_volumes())

        # And now delete and check same thing since list is cached as all
        # available
        fake_vol.status = 'deleting'
        fake_vol_dict = meta.obj_to_dict(fake_vol)

        def deleting_gone():
            def now_gone():
                cinder_mock.volumes.list.return_value = [fake_volb4]
                return mock.DEFAULT
            cinder_mock.volumes.list.side_effect = now_gone
            return mock.DEFAULT
        cinder_mock.volumes.list.return_value = [fake_volb4, fake_vol]
        cinder_mock.volumes.list.side_effect = deleting_gone
        cinder_mock.volumes.delete.return_value = fake_vol_dict
        self.cloud.delete_volume('12345')
        self.assertEqual([fake_volb4_dict], self.cloud.list_volumes())

    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_get_user_cache(self, keystone_mock):
        fake_user = fakes.FakeUser('999', '', '')
        keystone_mock.users.list.return_value = [fake_user]
        self.assertEqual({'999': fake_user}, self.cloud.get_user_cache())

    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_modify_user_invalidates_cache(self, keystone_mock):
        fake_user = fakes.FakeUser('abc123', 'abc123@domain.test',
                                   'abc123 name')
        # first cache an empty list
        keystone_mock.users.list.return_value = []
        self.assertEqual({}, self.cloud.get_user_cache())
        # now add one
        keystone_mock.users.list.return_value = [fake_user]
        keystone_mock.users.create.return_value = fake_user
        created = self.cloud.create_user(name='abc123 name',
                                         email='abc123@domain.test')
        self.assertEqual({'id': 'abc123',
                          'name': 'abc123 name',
                          'email': 'abc123@domain.test'}, created)
        # Cache should have been invalidated
        self.assertEqual({'abc123': fake_user}, self.cloud.get_user_cache())
        # Update and check to see if it is updated
        fake_user2 = fakes.FakeUser('abc123', 'abc123 name',
                                    'abc123-changed@domain.test')
        keystone_mock.users.update.return_value = fake_user2
        keystone_mock.users.list.return_value = [fake_user2]
        self.cloud.update_user('abc123', email='abc123-changed@domain.test')
        keystone_mock.users.update.assert_called_with(
            user=fake_user2, email='abc123-changed@domain.test')
        self.assertEqual({'abc123': fake_user2}, self.cloud.get_user_cache())
        # Now delete and ensure it disappears
        keystone_mock.users.list.return_value = []
        self.cloud.delete_user('abc123')
        self.assertEqual({}, self.cloud.get_user_cache())
        self.assertTrue(keystone_mock.users.delete.was_called)

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_list_flavors(self, nova_mock):
        nova_mock.flavors.list.return_value = []
        self.assertEqual([], self.cloud.list_flavors())

        fake_flavor = fakes.FakeFlavor('555', 'vanilla')
        fake_flavor_dict = meta.obj_to_dict(fake_flavor)
        nova_mock.flavors.list.return_value = [fake_flavor]
        self.cloud.list_flavors.invalidate(self.cloud)
        self.assertEqual([fake_flavor_dict], self.cloud.list_flavors())

    @mock.patch.object(shade.OpenStackCloud, 'glance_client')
    def test_list_images(self, glance_mock):
        glance_mock.images.list.return_value = []
        self.assertEqual([], self.cloud.list_images())

        fake_image = fakes.FakeImage('22', '22 name', 'success')
        fake_image_dict = meta.obj_to_dict(fake_image)
        glance_mock.images.list.return_value = [fake_image]
        self.cloud.list_images.invalidate(self.cloud)
        self.assertEqual([fake_image_dict], self.cloud.list_images())

    @mock.patch.object(shade.OpenStackCloud, 'glance_client')
    def test_list_images_ignores_unsteady_status(self, glance_mock):
        steady_image = fakes.FakeImage('68', 'Jagr', 'active')
        steady_image_dict = meta.obj_to_dict(steady_image)
        for status in ('queued', 'saving', 'pending_delete'):
            active_image = fakes.FakeImage(self.getUniqueString(),
                                           self.getUniqueString(), status)
            glance_mock.images.list.return_value = [active_image]
            active_image_dict = meta.obj_to_dict(active_image)
            self.assertEqual([active_image_dict],
                             self.cloud.list_images())
            glance_mock.images.list.return_value = [active_image, steady_image]
            # Should expect steady_image to appear if active wasn't cached
            self.assertEqual([active_image_dict, steady_image_dict],
                             self.cloud.list_images())

    @mock.patch.object(shade.OpenStackCloud, 'glance_client')
    def test_list_images_caches_steady_status(self, glance_mock):
        steady_image = fakes.FakeImage('91', 'Federov', 'active')
        first_image = None
        for status in ('active', 'deleted', 'killed'):
            active_image = fakes.FakeImage(self.getUniqueString(),
                                           self.getUniqueString(), status)
            active_image_dict = meta.obj_to_dict(active_image)
            if not first_image:
                first_image = active_image_dict
            glance_mock.images.list.return_value = [active_image]
            self.assertEqual([first_image], self.cloud.list_images())
            glance_mock.images.list.return_value = [active_image, steady_image]
            # because we skipped the create_image code path, no invalidation
            # was done, so we _SHOULD_ expect steady state images to cache and
            # therefore we should _not_ expect to see the new one here
            self.assertEqual([first_image], self.cloud.list_images())

    def _call_create_image(self, name, container=None):
        imagefile = tempfile.NamedTemporaryFile(delete=False)
        imagefile.write(b'\0')
        imagefile.close()
        self.cloud.create_image(
            name, imagefile.name, container=container, wait=True,
            is_public=False)

    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, 'glance_client')
    def test_create_image_put_v1(self, glance_mock, mock_api_version):
        mock_api_version.return_value = '1'
        glance_mock.images.list.return_value = []
        self.assertEqual([], self.cloud.list_images())

        fake_image = fakes.FakeImage('42', '42 name', 'success')
        glance_mock.images.create.return_value = fake_image
        glance_mock.images.list.return_value = [fake_image]
        self._call_create_image('42 name')
        args = {'name': '42 name',
                'container_format': 'bare', 'disk_format': 'qcow2',
                'properties': {'owner_specified.shade.md5': mock.ANY,
                               'owner_specified.shade.sha256': mock.ANY,
                               'is_public': False}}
        glance_mock.images.create.assert_called_with(**args)
        glance_mock.images.update.assert_called_with(data=mock.ANY,
                                                     image=fake_image)
        fake_image_dict = meta.obj_to_dict(fake_image)
        self.assertEqual([fake_image_dict], self.cloud.list_images())

    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, 'glance_client')
    def test_create_image_put_v2(self, glance_mock, mock_api_version):
        mock_api_version.return_value = '2'
        self.cloud.image_api_use_tasks = False

        glance_mock.images.list.return_value = []
        self.assertEqual([], self.cloud.list_images())

        fake_image = fakes.FakeImage('42', '42 name', 'success')
        glance_mock.images.create.return_value = fake_image
        glance_mock.images.list.return_value = [fake_image]
        self._call_create_image('42 name')
        args = {'name': '42 name',
                'container_format': 'bare', 'disk_format': 'qcow2',
                'owner_specified.shade.md5': mock.ANY,
                'owner_specified.shade.sha256': mock.ANY,
                'visibility': 'private'}
        glance_mock.images.create.assert_called_with(**args)
        glance_mock.images.upload.assert_called_with(
            image_data=mock.ANY, image_id=fake_image.id)
        fake_image_dict = meta.obj_to_dict(fake_image)
        self.assertEqual([fake_image_dict], self.cloud.list_images())

    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, '_get_file_hashes')
    @mock.patch.object(shade.OpenStackCloud, 'glance_client')
    @mock.patch.object(shade.OpenStackCloud, 'swift_client')
    @mock.patch.object(shade.OpenStackCloud, 'swift_service')
    def test_create_image_task(self,
                               swift_service_mock,
                               swift_mock,
                               glance_mock,
                               get_file_hashes,
                               mock_api_version):
        mock_api_version.return_value = '2'
        self.cloud.image_api_use_tasks = True

        class Container(object):
            name = 'image_upload_v2_test_container'

        fake_container = Container()
        swift_mock.get_capabilities.return_value = {
            'swift': {
                'max_file_size': 1000
            }
        }
        swift_mock.put_container.return_value = fake_container
        swift_mock.head_object.return_value = {}
        glance_mock.images.list.return_value = []
        self.assertEqual([], self.cloud.list_images())

        fake_md5 = "fake-md5"
        fake_sha256 = "fake-sha256"
        get_file_hashes.return_value = (fake_md5, fake_sha256)

        # V2's warlock objects just work like dicts
        class FakeImage(dict):
            status = 'CREATED'
            id = '99'
            name = '99 name'

        fake_image = FakeImage()
        fake_image.update({
            'id': '99',
            'name': '99 name',
            shade.IMAGE_MD5_KEY: fake_md5,
            shade.IMAGE_SHA256_KEY: fake_sha256,
        })
        glance_mock.images.list.return_value = [fake_image]

        class FakeTask(dict):
            status = 'success'
            result = {'image_id': '99'}

        fake_task = FakeTask()
        fake_task.update({
            'id': '100',
            'status': 'success',
        })
        glance_mock.tasks.get.return_value = fake_task
        self._call_create_image(name='99 name',
                                container='image_upload_v2_test_container')
        args = {'header': ['x-object-meta-x-shade-md5:fake-md5',
                           'x-object-meta-x-shade-sha256:fake-sha256'],
                'segment_size': 1000}
        swift_service_mock.upload.assert_called_with(
            container='image_upload_v2_test_container',
            objects=mock.ANY,
            options=args)
        glance_mock.tasks.create.assert_called_with(type='import', input={
            'import_from': 'image_upload_v2_test_container/99 name',
            'image_properties': {'name': '99 name'}})
        args = {'owner_specified.shade.md5': fake_md5,
                'owner_specified.shade.sha256': fake_sha256,
                'image_id': '99',
                'visibility': 'private'}
        glance_mock.images.update.assert_called_with(**args)
        fake_image_dict = meta.obj_to_dict(fake_image)
        self.assertEqual([fake_image_dict], self.cloud.list_images())

    @mock.patch.object(shade.OpenStackCloud, 'glance_client')
    def test_cache_no_cloud_name(self, glance_mock):
        class FakeImage(dict):
            id = 1
            status = 'active'
            name = 'None Test Image'
        fi = FakeImage(id=FakeImage.id, status=FakeImage.status,
                       name=FakeImage.name)
        glance_mock.images.list.return_value = [fi]
        self.cloud.name = None
        self.assertEqual([fi], [dict(x) for x in self.cloud.list_images()])
        # Now test that the list was cached
        fi2 = FakeImage(id=2, status=FakeImage.status, name=FakeImage.name)
        fi2.id = 2
        glance_mock.images.list.return_value = [fi, fi2]
        self.assertEqual([fi], [dict(x) for x in self.cloud.list_images()])
        # Invalidation too
        self.cloud.list_images.invalidate(self.cloud)
        self.assertEqual(
            [fi, fi2], [dict(x) for x in self.cloud.list_images()])


class TestBogusAuth(base.TestCase):
    CONFIG = {
        'clouds':
        {
            '_bogus_test_':
            {
                'auth_type': 'bogus',
                'auth':
                {
                    'auth_url': 'http://198.51.100.1:35357/v2.0',
                    'username': '_test_user_',
                    'password': '_test_pass_',
                    'project_name': '_test_project_',
                },
                'region_name': '_test_region_',
            },
        },
    }

    def setUp(self):
        super(TestBogusAuth, self).setUp()

        # Isolate os-client-config from test environment
        config = tempfile.NamedTemporaryFile(delete=False)
        config.write(bytes(yaml.dump(self.CONFIG).encode('utf-8')))
        config.close()
        vendor = tempfile.NamedTemporaryFile(delete=False)
        vendor.write(b'{}')
        vendor.close()

        self.cloud_config = occ.OpenStackConfig(config_files=[config.name],
                                                vendor_files=[vendor.name])

    def test_get_auth_bogus(self):
        with testtools.ExpectedException(exc.OpenStackCloudException):
            shade.openstack_cloud(
                cloud='_bogus_test_', config=self.cloud_config)
