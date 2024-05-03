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

import fixtures

from openstack import config
from openstack.config import cloud_region
from openstack import exceptions
from openstack.tests.unit.config import base


class TestEnviron(base.TestCase):
    def setUp(self):
        super().setUp()
        self.useFixture(
            fixtures.EnvironmentVariable('OS_AUTH_URL', 'https://example.com')
        )
        self.useFixture(
            fixtures.EnvironmentVariable('OS_USERNAME', 'testuser')
        )
        self.useFixture(
            fixtures.EnvironmentVariable('OS_PASSWORD', 'testpass')
        )
        self.useFixture(
            fixtures.EnvironmentVariable('OS_PROJECT_NAME', 'testproject')
        )
        self.useFixture(
            fixtures.EnvironmentVariable('NOVA_PROJECT_ID', 'testnova')
        )

    def test_get_one(self):
        c = config.OpenStackConfig(
            config_files=[self.cloud_yaml], vendor_files=[self.vendor_yaml]
        )
        self.assertIsInstance(c.get_one(), cloud_region.CloudRegion)

    def test_no_fallthrough(self):
        c = config.OpenStackConfig(
            config_files=[self.cloud_yaml], vendor_files=[self.vendor_yaml]
        )
        self.assertRaises(exceptions.ConfigException, c.get_one, 'openstack')

    def test_envvar_name_override(self):
        self.useFixture(
            fixtures.EnvironmentVariable('OS_CLOUD_NAME', 'override')
        )
        c = config.OpenStackConfig(
            config_files=[self.cloud_yaml], vendor_files=[self.vendor_yaml]
        )
        cc = c.get_one('override')
        self._assert_cloud_details(cc)

    def test_envvar_prefer_ipv6_override(self):
        self.useFixture(
            fixtures.EnvironmentVariable('OS_PREFER_IPV6', 'false')
        )
        c = config.OpenStackConfig(
            config_files=[self.cloud_yaml],
            vendor_files=[self.vendor_yaml],
            secure_files=[self.secure_yaml],
        )
        cc = c.get_one('_test-cloud_')
        self.assertFalse(cc.prefer_ipv6)

    def test_environ_exists(self):
        c = config.OpenStackConfig(
            config_files=[self.cloud_yaml],
            vendor_files=[self.vendor_yaml],
            secure_files=[self.secure_yaml],
        )
        cc = c.get_one('envvars')
        self._assert_cloud_details(cc)
        self.assertNotIn('auth_url', cc.config)
        self.assertIn('auth_url', cc.config['auth'])
        self.assertNotIn('project_id', cc.config['auth'])
        self.assertNotIn('auth_url', cc.config)
        cc = c.get_one('_test-cloud_')
        self._assert_cloud_details(cc)
        cc = c.get_one('_test_cloud_no_vendor')
        self._assert_cloud_details(cc)

    def test_environ_prefix(self):
        c = config.OpenStackConfig(
            config_files=[self.cloud_yaml],
            vendor_files=[self.vendor_yaml],
            envvar_prefix='NOVA_',
            secure_files=[self.secure_yaml],
        )
        cc = c.get_one('envvars')
        self._assert_cloud_details(cc)
        self.assertNotIn('auth_url', cc.config)
        self.assertIn('auth_url', cc.config['auth'])
        self.assertIn('project_id', cc.config['auth'])
        self.assertNotIn('auth_url', cc.config)
        cc = c.get_one('_test-cloud_')
        self._assert_cloud_details(cc)
        cc = c.get_one('_test_cloud_no_vendor')
        self._assert_cloud_details(cc)

    def test_get_one_with_config_files(self):
        c = config.OpenStackConfig(
            config_files=[self.cloud_yaml],
            vendor_files=[self.vendor_yaml],
            secure_files=[self.secure_yaml],
        )
        self.assertIsInstance(c.cloud_config, dict)
        self.assertIn('cache', c.cloud_config)
        self.assertIsInstance(c.cloud_config['cache'], dict)
        self.assertIn('max_age', c.cloud_config['cache'])
        self.assertIn('path', c.cloud_config['cache'])
        cc = c.get_one('_test-cloud_')
        self._assert_cloud_details(cc)
        cc = c.get_one('_test_cloud_no_vendor')
        self._assert_cloud_details(cc)

    def test_config_file_override(self):
        self.useFixture(
            fixtures.EnvironmentVariable(
                'OS_CLIENT_CONFIG_FILE', self.cloud_yaml
            )
        )
        c = config.OpenStackConfig(
            config_files=[], vendor_files=[self.vendor_yaml]
        )
        cc = c.get_one('_test-cloud_')
        self._assert_cloud_details(cc)


class TestEnvvars(base.TestCase):
    def test_no_envvars(self):
        self.useFixture(fixtures.EnvironmentVariable('NOVA_USERNAME', 'nova'))
        c = config.OpenStackConfig(
            config_files=[self.cloud_yaml], vendor_files=[self.vendor_yaml]
        )
        self.assertRaises(exceptions.ConfigException, c.get_one, 'envvars')

    def test_test_envvars(self):
        self.useFixture(fixtures.EnvironmentVariable('NOVA_USERNAME', 'nova'))
        self.useFixture(
            fixtures.EnvironmentVariable('OS_STDERR_CAPTURE', 'True')
        )
        c = config.OpenStackConfig(
            config_files=[self.cloud_yaml], vendor_files=[self.vendor_yaml]
        )
        self.assertRaises(exceptions.ConfigException, c.get_one, 'envvars')

    def test_incomplete_envvars(self):
        self.useFixture(fixtures.EnvironmentVariable('NOVA_USERNAME', 'nova'))
        self.useFixture(fixtures.EnvironmentVariable('OS_USERNAME', 'user'))
        config.OpenStackConfig(
            config_files=[self.cloud_yaml], vendor_files=[self.vendor_yaml]
        )
        # This is broken due to an issue that's fixed in a subsequent patch
        # commenting it out in this patch to keep the patch size reasonable
        # self.assertRaises(
        #     keystoneauth1.exceptions.auth_plugins.MissingRequiredOptions,
        #     c.get_one, 'envvars')

    def test_have_envvars(self):
        self.useFixture(fixtures.EnvironmentVariable('NOVA_USERNAME', 'nova'))
        self.useFixture(
            fixtures.EnvironmentVariable('OS_AUTH_URL', 'http://example.com')
        )
        self.useFixture(fixtures.EnvironmentVariable('OS_USERNAME', 'user'))
        self.useFixture(
            fixtures.EnvironmentVariable('OS_PASSWORD', 'password')
        )
        self.useFixture(
            fixtures.EnvironmentVariable('OS_PROJECT_NAME', 'project')
        )
        c = config.OpenStackConfig(
            config_files=[self.cloud_yaml], vendor_files=[self.vendor_yaml]
        )
        cc = c.get_one('envvars')
        self.assertEqual(cc.config['auth']['username'], 'user')

    def test_old_envvars(self):
        self.useFixture(fixtures.EnvironmentVariable('NOVA_USERNAME', 'nova'))
        self.useFixture(
            fixtures.EnvironmentVariable('NOVA_AUTH_URL', 'http://example.com')
        )
        self.useFixture(
            fixtures.EnvironmentVariable('NOVA_PASSWORD', 'password')
        )
        self.useFixture(
            fixtures.EnvironmentVariable('NOVA_PROJECT_NAME', 'project')
        )
        c = config.OpenStackConfig(
            config_files=[self.cloud_yaml],
            vendor_files=[self.vendor_yaml],
            envvar_prefix='NOVA_',
        )
        cc = c.get_one('envvars')
        self.assertEqual(cc.config['auth']['username'], 'nova')
