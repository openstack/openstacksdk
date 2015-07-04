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


from os_client_config import cloud_config
from os_client_config import config
from os_client_config import exceptions
from os_client_config.tests import base

import fixtures


class TestEnviron(base.TestCase):

    def setUp(self):
        super(TestEnviron, self).setUp()
        self.useFixture(
            fixtures.EnvironmentVariable('OS_AUTH_URL', 'https://example.com'))
        self.useFixture(
            fixtures.EnvironmentVariable('OS_USERNAME', 'testuser'))
        self.useFixture(
            fixtures.EnvironmentVariable('OS_PROJECT_NAME', 'testproject'))

    def test_get_one_cloud(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        self.assertIsInstance(c.get_one_cloud(), cloud_config.CloudConfig)

    def test_no_fallthrough(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        self.assertRaises(
            exceptions.OpenStackConfigException, c.get_one_cloud, 'openstack')

    def test_envvar_name_override(self):
        self.useFixture(
            fixtures.EnvironmentVariable('OS_CLOUD_NAME', 'override'))
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        cc = c.get_one_cloud('override')
        self._assert_cloud_details(cc)

    def test_envvar_prefer_ipv6_override(self):
        self.useFixture(
            fixtures.EnvironmentVariable('OS_PREFER_IPV6', 'false'))
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        cc = c.get_one_cloud('_test-cloud_')
        self.assertFalse(cc.prefer_ipv6)

    def test_environ_exists(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        cc = c.get_one_cloud('envvars')
        self._assert_cloud_details(cc)
        self.assertNotIn('auth_url', cc.config)
        self.assertIn('auth_url', cc.config['auth'])
        self.assertNotIn('auth_url', cc.config)
        cc = c.get_one_cloud('_test-cloud_')
        self._assert_cloud_details(cc)
        cc = c.get_one_cloud('_test_cloud_no_vendor')
        self._assert_cloud_details(cc)

    def test_get_one_cloud_with_config_files(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        self.assertIsInstance(c.cloud_config, dict)
        self.assertIn('cache', c.cloud_config)
        self.assertIsInstance(c.cloud_config['cache'], dict)
        self.assertIn('max_age', c.cloud_config['cache'])
        self.assertIn('path', c.cloud_config['cache'])
        cc = c.get_one_cloud('_test-cloud_')
        self._assert_cloud_details(cc)
        cc = c.get_one_cloud('_test_cloud_no_vendor')
        self._assert_cloud_details(cc)

    def test_config_file_override(self):
        self.useFixture(
            fixtures.EnvironmentVariable(
                'OS_CLIENT_CONFIG_FILE', self.cloud_yaml))
        c = config.OpenStackConfig(config_files=[],
                                   vendor_files=[self.vendor_yaml])
        cc = c.get_one_cloud('_test-cloud_')
        self._assert_cloud_details(cc)
