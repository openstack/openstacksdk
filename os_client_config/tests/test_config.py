# Copyright (c) 2014 Hewlett-Packard Development Company, L.P.
#
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

import extras
import fixtures
import testtools
import yaml

from os_client_config import cloud_config
from os_client_config import config


class TestConfig(testtools.TestCase):
    def get_config(self):
        config = {
            'clouds': {
                '_test_cloud_': {
                    'auth': {
                        'username': 'testuser',
                        'password': 'testpass',
                        'project_name': 'testproject',
                    },
                    'region_name': 'test-region',
                },
            },
            'cache': {'max_age': 1},
        }
        tdir = self.useFixture(fixtures.TempDir())
        config['cache']['path'] = tdir.path
        return config

    def test_get_one_cloud(self):
        c = config.OpenStackConfig()
        self.assertIsInstance(c.get_one_cloud(), cloud_config.CloudConfig)

    def test_get_one_cloud_with_config_files(self):
        self.useFixture(fixtures.NestedTempfile())
        with tempfile.NamedTemporaryFile() as cloud_yaml:
            cloud_yaml.write(yaml.safe_dump(self.get_config()).encode('utf-8'))
            cloud_yaml.flush()
            c = config.OpenStackConfig(config_files=[cloud_yaml.name])
        self.assertIsInstance(c.cloud_config, dict)
        self.assertIn('cache', c.cloud_config)
        self.assertIsInstance(c.cloud_config['cache'], dict)
        self.assertIn('max_age', c.cloud_config['cache'])
        self.assertIn('path', c.cloud_config['cache'])
        cc = c.get_one_cloud('_test_cloud_')
        self.assertIsInstance(cc, cloud_config.CloudConfig)
        self.assertTrue(extras.safe_hasattr(cc, 'auth'))
        self.assertIsInstance(cc.auth, dict)
        self.assertIn('username', cc.auth)
        self.assertEqual('testuser', cc.auth['username'])
