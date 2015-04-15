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
from shade.tests import base


class TestMemoryCache(base.TestCase):

    CACHING_CONFIG = {
        'cache':
        {
            'max_age': 10,
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
        self.cloud = shade.openstack_cloud(config=self.cloud_config)

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
        cinder_mock.volumes.list.return_value = [mock_volume]
        self.assertEqual([mock_volume], self.cloud.list_volumes())
        mock_volume2 = mock.MagicMock()
        mock_volume2.id = 'volume2'
        mock_volume2.status = 'available'
        mock_volume2.display_name = 'Volume 2 Display Name'
        cinder_mock.volumes.list.return_value = [mock_volume, mock_volume2]
        self.assertEqual([mock_volume], self.cloud.list_volumes())
        self.cloud.list_volumes.invalidate(self.cloud)
        self.assertEqual([mock_volume, mock_volume2],
                         self.cloud.list_volumes())

    @mock.patch('shade.OpenStackCloud.cinder_client')
    def test_list_volumes_creating_invalidates(self, cinder_mock):
        mock_volume = mock.MagicMock()
        mock_volume.id = 'volume1'
        mock_volume.status = 'creating'
        mock_volume.display_name = 'Volume 1 Display Name'
        cinder_mock.volumes.list.return_value = [mock_volume]
        self.assertEqual([mock_volume], self.cloud.list_volumes())
        mock_volume2 = mock.MagicMock()
        mock_volume2.id = 'volume2'
        mock_volume2.status = 'available'
        mock_volume2.display_name = 'Volume 2 Display Name'
        cinder_mock.volumes.list.return_value = [mock_volume, mock_volume2]
        self.assertEqual([mock_volume, mock_volume2],
                         self.cloud.list_volumes())

    @mock.patch.object(shade.OpenStackCloud, 'cinder_client')
    def test_create_volume_invalidates(self, cinder_mock):
        mock_volb4 = mock.MagicMock()
        mock_volb4.id = 'volume1'
        mock_volb4.status = 'available'
        mock_volb4.display_name = 'Volume 1 Display Name'
        cinder_mock.volumes.list.return_value = [mock_volb4]
        self.assertEqual([mock_volb4], self.cloud.list_volumes())
        volume = dict(display_name='junk_vol',
                      size=1,
                      display_description='test junk volume')
        mock_vol = mock.Mock()
        mock_vol.status = 'creating'
        mock_vol.id = '12345'
        cinder_mock.volumes.create.return_value = mock_vol
        cinder_mock.volumes.list.return_value = [mock_volb4, mock_vol]

        def creating_available():
            def now_available():
                mock_vol.status = 'available'
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
        self.assertEqual([mock_volb4, mock_vol], self.cloud.list_volumes())
