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

import os

import fixtures

from os_client_config import cloud_config
from os_client_config import config
from os_client_config import defaults
from os_client_config import exceptions
from os_client_config.tests import base


class TestConfig(base.TestCase):

    def test_get_one_cloud(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        self.assertIsInstance(c.get_one_cloud(), cloud_config.CloudConfig)

    def test_get_one_cloud_auth_defaults(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml])
        cc = c.get_one_cloud(cloud='_test_cloud_', auth={'username': 'user'})
        self.assertEqual('user', cc.auth['username'])
        self.assertEqual(
            defaults._defaults['auth_type'],
            cc.auth_type,
        )
        self.assertEqual(
            defaults._defaults['identity_api_version'],
            cc.identity_api_version,
        )

    def test_get_one_cloud_auth_override_defaults(self):
        default_options = {'auth_type': 'token'}
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   override_defaults=default_options)
        cc = c.get_one_cloud(cloud='_test_cloud_', auth={'username': 'user'})
        self.assertEqual('user', cc.auth['username'])
        self.assertEqual('token', cc.auth_type)
        self.assertEqual(
            defaults._defaults['identity_api_version'],
            cc.identity_api_version,
        )

    def test_get_one_cloud_with_config_files(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        self.assertIsInstance(c.cloud_config, dict)
        self.assertIn('cache', c.cloud_config)
        self.assertIsInstance(c.cloud_config['cache'], dict)
        self.assertIn('max_age', c.cloud_config['cache'])
        self.assertIn('path', c.cloud_config['cache'])
        cc = c.get_one_cloud('_test_cloud_')
        self._assert_cloud_details(cc)
        cc = c.get_one_cloud('_test_cloud_no_vendor')
        self._assert_cloud_details(cc)

    def test_no_environ(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        self.assertRaises(
            exceptions.OpenStackConfigException, c.get_one_cloud, 'envvars')

    def test_fallthrough(self):
        c = config.OpenStackConfig(config_files=[self.no_yaml],
                                   vendor_files=[self.no_yaml])
        for k in os.environ.keys():
            if k.startswith('OS_'):
                self.useFixture(fixtures.EnvironmentVariable(k))
        c.get_one_cloud(cloud='defaults')

    def test_get_one_cloud_auth_merge(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml])
        cc = c.get_one_cloud(cloud='_test_cloud_', auth={'username': 'user'})
        self.assertEqual('user', cc.auth['username'])
        self.assertEqual('testpass', cc.auth['password'])
