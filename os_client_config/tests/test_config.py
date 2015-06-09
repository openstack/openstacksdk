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

import argparse
import copy
import os

import fixtures
import yaml

from os_client_config import cloud_config
from os_client_config import config
from os_client_config import defaults
from os_client_config import exceptions
from os_client_config.tests import base


class TestConfig(base.TestCase):

    def test_get_all_clouds(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        clouds = c.get_all_clouds()
        user_clouds = [cloud for cloud in base.USER_CONF['clouds'].keys()]
        configured_clouds = [cloud.name for cloud in clouds]
        self.assertItemsEqual(user_clouds, configured_clouds)

    def test_get_one_cloud(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        cloud = c.get_one_cloud()
        self.assertIsInstance(cloud, cloud_config.CloudConfig)
        self.assertEqual(cloud.name, '')

    def test_get_one_cloud_auth_defaults(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml])
        cc = c.get_one_cloud(cloud='_test-cloud_', auth={'username': 'user'})
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
        cc = c.get_one_cloud(cloud='_test-cloud_', auth={'username': 'user'})
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
        cc = c.get_one_cloud('_test-cloud_')
        self._assert_cloud_details(cc)
        cc = c.get_one_cloud('_test_cloud_no_vendor')
        self._assert_cloud_details(cc)

    def test_get_one_cloud_with_int_project_id(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        cc = c.get_one_cloud('_test-cloud-int-project_')
        self.assertEqual('12345', cc.auth['project_name'])

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
        cc = c.get_one_cloud(cloud='_test-cloud_', auth={'username': 'user'})
        self.assertEqual('user', cc.auth['username'])
        self.assertEqual('testpass', cc.auth['password'])

    def test_get_cloud_names(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml])
        self.assertEqual(
            ['_test-cloud-int-project_',
             '_test-cloud_',
             '_test_cloud_no_vendor',
             ],
            sorted(c.get_cloud_names()))
        c = config.OpenStackConfig(config_files=[self.no_yaml],
                                   vendor_files=[self.no_yaml])
        for k in os.environ.keys():
            if k.startswith('OS_'):
                self.useFixture(fixtures.EnvironmentVariable(k))
        c.get_one_cloud(cloud='defaults')
        self.assertEqual(['defaults'], sorted(c.get_cloud_names()))

    def test_set_one_cloud_creates_file(self):
        config_dir = fixtures.TempDir()
        self.useFixture(config_dir)
        config_path = os.path.join(config_dir.path, 'clouds.yaml')
        config.OpenStackConfig.set_one_cloud(config_path, '_test_cloud_')
        self.assertTrue(os.path.isfile(config_path))
        with open(config_path) as fh:
            self.assertEqual({'clouds': {'_test_cloud_': {}}},
                             yaml.safe_load(fh))

    def test_set_one_cloud_updates_cloud(self):
        new_config = {
            'cloud': 'new_cloud',
            'auth': {
                'password': 'newpass'
            }
        }

        resulting_cloud_config = {
            'auth': {
                'password': 'newpass',
                'username': 'testuser'
            },
            'cloud': 'new_cloud',
            'profile': '_test_cloud_in_our_cloud',
            'region_name': 'test-region'
        }
        resulting_config = copy.deepcopy(base.USER_CONF)
        resulting_config['clouds']['_test-cloud_'] = resulting_cloud_config
        config.OpenStackConfig.set_one_cloud(self.cloud_yaml, '_test-cloud_',
                                             new_config)
        with open(self.cloud_yaml) as fh:
            written_config = yaml.safe_load(fh)
            self.assertEqual(written_config, resulting_config)


class TestConfigArgparse(base.TestCase):

    def setUp(self):
        super(TestConfigArgparse, self).setUp()

        self.options = argparse.Namespace(
            region_name='other-test-region',
            snack_type='cookie',
        )

    def test_get_one_cloud_argparse(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])

        cc = c.get_one_cloud(cloud='_test-cloud_', argparse=self.options)
        self._assert_cloud_details(cc)
        self.assertEqual(cc.region_name, 'other-test-region')
        self.assertEqual(cc.snack_type, 'cookie')

    def test_get_one_cloud_just_argparse(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])

        cc = c.get_one_cloud(cloud='', argparse=self.options)
        self.assertIsNone(cc.cloud)
        self.assertNotIn('username', cc.auth)
        self.assertEqual(cc.region_name, 'other-test-region')
        self.assertEqual(cc.snack_type, 'cookie')

    def test_get_one_cloud_no_argparse(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])

        cc = c.get_one_cloud(cloud='_test-cloud_', argparse=None)
        self._assert_cloud_details(cc)
        self.assertEqual(cc.region_name, 'test-region')
        self.assertIsNone(cc.snack_type)

    def test_fix_env_args(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])

        env_args = {'os-compute-api-version': 1}
        fixed_args = c._fix_args(env_args)

        self.assertDictEqual({'compute_api_version': 1}, fixed_args)


class TestConfigDefault(base.TestCase):

    def test_set_no_default(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        cc = c.get_one_cloud(cloud='_test-cloud_', argparse=None)
        self._assert_cloud_details(cc)
        self.assertEqual(cc.auth_type, 'password')
