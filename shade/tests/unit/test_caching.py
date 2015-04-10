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
