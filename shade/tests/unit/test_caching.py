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
import yaml

import shade
from shade import meta
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
        mock_project = mock.MagicMock()
        mock_project.id = 'project_a'
        keystone_mock.projects.list.return_value = [mock_project]
        self.assertEqual({'project_a': mock_project}, self.cloud.project_cache)
        mock_project_b = mock.MagicMock()
        mock_project_b.id = 'project_b'
        keystone_mock.projects.list.return_value = [mock_project,
                                                    mock_project_b]
        self.assertEqual(
            {'project_a': mock_project}, self.cloud.project_cache)
        self.cloud.get_project_cache.invalidate(self.cloud)
        self.assertEqual(
            {'project_a': mock_project,
             'project_b': mock_project_b}, self.cloud.project_cache)

    @mock.patch('shade.OpenStackCloud.cinder_client')
    def test_list_volumes(self, cinder_mock):
        mock_volume = mock.MagicMock()
        mock_volume.id = 'volume1'
        mock_volume.status = 'available'
        mock_volume.display_name = 'Volume 1 Display Name'
        mock_volume_dict = meta.obj_to_dict(mock_volume)
        cinder_mock.volumes.list.return_value = [mock_volume]
        self.assertEqual([mock_volume_dict], self.cloud.list_volumes())
        mock_volume2 = mock.MagicMock()
        mock_volume2.id = 'volume2'
        mock_volume2.status = 'available'
        mock_volume2.display_name = 'Volume 2 Display Name'
        mock_volume2_dict = meta.obj_to_dict(mock_volume2)
        cinder_mock.volumes.list.return_value = [mock_volume, mock_volume2]
        self.assertEqual([mock_volume_dict], self.cloud.list_volumes())
        self.cloud.list_volumes.invalidate(self.cloud)
        self.assertEqual([mock_volume_dict, mock_volume2_dict],
                         self.cloud.list_volumes())

    @mock.patch('shade.OpenStackCloud.cinder_client')
    def test_list_volumes_creating_invalidates(self, cinder_mock):
        mock_volume = mock.MagicMock()
        mock_volume.id = 'volume1'
        mock_volume.status = 'creating'
        mock_volume.display_name = 'Volume 1 Display Name'
        mock_volume_dict = meta.obj_to_dict(mock_volume)
        cinder_mock.volumes.list.return_value = [mock_volume]
        self.assertEqual([mock_volume_dict], self.cloud.list_volumes())
        mock_volume2 = mock.MagicMock()
        mock_volume2.id = 'volume2'
        mock_volume2.status = 'available'
        mock_volume2.display_name = 'Volume 2 Display Name'
        mock_volume2_dict = meta.obj_to_dict(mock_volume2)
        cinder_mock.volumes.list.return_value = [mock_volume, mock_volume2]
        self.assertEqual([mock_volume_dict, mock_volume2_dict],
                         self.cloud.list_volumes())

    @mock.patch.object(shade.OpenStackCloud, 'cinder_client')
    def test_create_volume_invalidates(self, cinder_mock):
        mock_volb4 = mock.MagicMock()
        mock_volb4.id = 'volume1'
        mock_volb4.status = 'available'
        mock_volb4.display_name = 'Volume 1 Display Name'
        mock_volb4_dict = meta.obj_to_dict(mock_volb4)
        cinder_mock.volumes.list.return_value = [mock_volb4]
        self.assertEqual([mock_volb4_dict], self.cloud.list_volumes())
        volume = dict(display_name='junk_vol',
                      size=1,
                      display_description='test junk volume')
        mock_vol = mock.Mock()
        mock_vol.status = 'creating'
        mock_vol.id = '12345'
        mock_vol_dict = meta.obj_to_dict(mock_vol)
        cinder_mock.volumes.create.return_value = mock_vol
        cinder_mock.volumes.list.return_value = [mock_volb4, mock_vol]

        def creating_available():
            def now_available():
                mock_vol.status = 'available'
                mock_vol_dict['status'] = 'available'
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
        self.assertEqual([mock_volb4_dict, mock_vol_dict],
                         self.cloud.list_volumes())

        # And now delete and check same thing since list is cached as all
        # available
        mock_vol.status = 'deleting'
        mock_vol_dict = meta.obj_to_dict(mock_vol)

        def deleting_gone():
            def now_gone():
                cinder_mock.volumes.list.return_value = [mock_volb4]
                return mock.DEFAULT
            cinder_mock.volumes.list.side_effect = now_gone
            return mock.DEFAULT
        cinder_mock.volumes.list.return_value = [mock_volb4, mock_vol]
        cinder_mock.volumes.list.side_effect = deleting_gone
        cinder_mock.volumes.delete.return_value = mock_vol_dict
        self.cloud.delete_volume('12345')
        self.assertEqual([mock_volb4_dict], self.cloud.list_volumes())

    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_get_user_cache(self, keystone_mock):
        mock_user = mock.MagicMock()
        mock_user.id = '999'
        keystone_mock.users.list.return_value = [mock_user]
        self.assertEqual({'999': mock_user}, self.cloud.get_user_cache())

    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_modify_user_invalidates_cache(self, keystone_mock):
        class User(object):
            id = 'abc123'
            email = 'abc123@domain.test'
            name = 'abc123 name'
        fake_user = User()
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
        fake_user2 = User()
        fake_user2.email = 'abc123-changed@domain.test'
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

        class Flavor(object):
            id = '555'
            name = 'vanilla'
        fake_flavor = Flavor()
        fake_flavor_dict = meta.obj_to_dict(fake_flavor)
        nova_mock.flavors.list.return_value = [fake_flavor]
        self.cloud.list_flavors.invalidate(self.cloud)
        self.assertEqual([fake_flavor_dict], self.cloud.list_flavors())

    @mock.patch.object(shade.OpenStackCloud, 'glance_client')
    def test_list_images(self, glance_mock):
        glance_mock.images.list.return_value = []
        self.assertEqual({}, self.cloud.list_images())

        class Image(object):
            id = '22'
            name = '22 name'
            status = 'success'
        fake_image = Image()
        glance_mock.images.list.return_value = [fake_image]
        self.cloud.list_images.invalidate(self.cloud)
        self.assertEqual({'22': fake_image}, self.cloud.list_images())

    @mock.patch.object(shade.OpenStackCloud, 'glance_client')
    def test_list_images_ignores_unsteady_status(self, glance_mock):
        class Image(object):
            id = None
            name = None
            status = None
        steady_image = Image()
        steady_image.id = '68'
        steady_image.name = 'Jagr'
        steady_image.status = 'active'
        for status in ('queued', 'saving', 'pending_delete'):
            active_image = Image()
            active_image.id = self.getUniqueString()
            active_image.name = self.getUniqueString()
            active_image.status = status
            glance_mock.images.list.return_value = [active_image]
            self.assertEqual({active_image.id: active_image},
                             self.cloud.list_images())
            glance_mock.images.list.return_value = [active_image, steady_image]
            # Should expect steady_image to appear if active wasn't cached
            self.assertEqual({active_image.id: active_image,
                              '68': steady_image},
                             self.cloud.list_images())

    @mock.patch.object(shade.OpenStackCloud, 'glance_client')
    def test_list_images_caches_steady_status(self, glance_mock):
        class Image(object):
            id = None
            name = None
            status = None
        steady_image = Image()
        steady_image.id = '91'
        steady_image.name = 'Federov'
        steady_image.status = 'active'
        first_image = None
        for status in ('active', 'deleted', 'killed'):
            active_image = Image()
            active_image.id = self.getUniqueString()
            active_image.name = self.getUniqueString()
            active_image.status = status
            if not first_image:
                first_image = active_image
            glance_mock.images.list.return_value = [active_image]
            self.assertEqual({first_image.id: first_image},
                             self.cloud.list_images())
            glance_mock.images.list.return_value = [active_image, steady_image]
            # because we skipped the create_image code path, no invalidation
            # was done, so we _SHOULD_ expect steady state images to cache and
            # therefore we should _not_ expect to see the new one here
            self.assertEqual({first_image.id: first_image},
                             self.cloud.list_images())

    def _call_create_image(self, name, container=None):
        imagefile = tempfile.NamedTemporaryFile(delete=False)
        imagefile.write(b'\0')
        imagefile.close()
        self.cloud.create_image(
            name, imagefile.name, container=container, wait=True)

    @mock.patch.object(shade.OpenStackCloud, 'glance_client')
    def test_create_image_put(self, glance_mock):
        self.cloud.api_versions['image'] = '1'
        glance_mock.images.list.return_value = []
        self.assertEqual({}, self.cloud.list_images())

        class Image(object):
            id = '42'
            name = '42 name'
            status = 'success'
        fake_image = Image()
        glance_mock.images.create.return_value = fake_image
        glance_mock.images.list.return_value = [fake_image]
        self._call_create_image('42 name')
        args = {'name': '42 name',
                'properties': {'owner_specified.shade.md5': mock.ANY,
                               'owner_specified.shade.sha256': mock.ANY}}
        glance_mock.images.create.assert_called_with(**args)
        glance_mock.images.update.assert_called_with(data=mock.ANY,
                                                     image=fake_image)
        self.assertEqual({'42': fake_image}, self.cloud.list_images())

    @mock.patch.object(shade.OpenStackCloud, 'glance_client')
    @mock.patch.object(shade.OpenStackCloud, 'swift_client')
    def test_create_image_task(self, swift_mock, glance_mock):
        self.cloud.api_versions['image'] = '2'
        self.cloud.image_api_use_tasks = True

        class Container(object):
            name = 'image_upload_v2_test_container'

        fake_container = Container()
        swift_mock.put_container.return_value = fake_container
        swift_mock.head_object.return_value = {}
        glance_mock.images.list.return_value = []
        self.assertEqual({}, self.cloud.list_images())

        # V2's warlock objects just work like dicts
        class FakeImage(dict):
            status = 'CREATED'
            id = '99'
            name = '99 name'

        fake_image = FakeImage()
        fake_image.update({
            'id': '99',
            'name': '99 name',
            shade.IMAGE_MD5_KEY: '',
            shade.IMAGE_SHA256_KEY: '',
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
        args = {'headers': {'x-object-meta-x-shade-md5': mock.ANY,
                            'x-object-meta-x-shade-sha256': mock.ANY},
                'obj': '99 name',
                'container': 'image_upload_v2_test_container'}
        swift_mock.post_object.assert_called_with(**args)
        swift_mock.put_object.assert_called_with(
            contents=mock.ANY,
            obj='99 name',
            container='image_upload_v2_test_container')
        glance_mock.tasks.create.assert_called_with(type='import', input={
            'import_from': 'image_upload_v2_test_container/99 name',
            'image_properties': {'name': '99 name'}})
        args = {'owner_specified.shade.md5': mock.ANY,
                'owner_specified.shade.sha256': mock.ANY,
                'image_id': '99'}
        glance_mock.images.update.assert_called_with(**args)
        self.assertEqual({'99': fake_image}, self.cloud.list_images())
