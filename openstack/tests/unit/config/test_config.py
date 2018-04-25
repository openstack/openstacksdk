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

import extras
import fixtures
import testtools
import yaml

from openstack import config
from openstack.config import cloud_region
from openstack.config import defaults
from openstack import exceptions
from openstack.tests.unit.config import base


def prompt_for_password(prompt=None):
    """Fake prompt function that just returns a constant string"""
    return 'promptpass'


class TestConfig(base.TestCase):

    def test_get_all(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml],
                                   secure_files=[self.no_yaml])
        clouds = c.get_all()
        # We add one by hand because the regions cloud is going to exist
        # twice since it has two regions in it
        user_clouds = [
            cloud for cloud in base.USER_CONF['clouds'].keys()
        ] + ['_test_cloud_regions']
        configured_clouds = [cloud.name for cloud in clouds]
        self.assertItemsEqual(user_clouds, configured_clouds)

    def test_get_all_clouds(self):
        # Ensure the alias is in place
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml],
                                   secure_files=[self.no_yaml])
        clouds = c.get_all_clouds()
        # We add one by hand because the regions cloud is going to exist
        # twice since it has two regions in it
        user_clouds = [
            cloud for cloud in base.USER_CONF['clouds'].keys()
        ] + ['_test_cloud_regions']
        configured_clouds = [cloud.name for cloud in clouds]
        self.assertItemsEqual(user_clouds, configured_clouds)

    def test_get_one(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        cloud = c.get_one(validate=False)
        self.assertIsInstance(cloud, cloud_region.CloudRegion)
        self.assertEqual(cloud.name, '')

    def test_get_one_cloud(self):
        # Ensure the alias is in place
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        cloud = c.get_one_cloud(validate=False)
        self.assertIsInstance(cloud, cloud_region.CloudRegion)
        self.assertEqual(cloud.name, '')

    def test_get_one_default_cloud_from_file(self):
        single_conf = base._write_yaml({
            'clouds': {
                'single': {
                    'auth': {
                        'auth_url': 'http://example.com/v2',
                        'username': 'testuser',
                        'password': 'testpass',
                        'project_name': 'testproject',
                    },
                    'region_name': 'test-region',
                }
            }
        })
        c = config.OpenStackConfig(config_files=[single_conf],
                                   vendor_files=[self.vendor_yaml])
        cc = c.get_one()
        self.assertEqual(cc.name, 'single')

    def test_get_one_auth_defaults(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml])
        cc = c.get_one(cloud='_test-cloud_', auth={'username': 'user'})
        self.assertEqual('user', cc.auth['username'])
        self.assertEqual(
            defaults._defaults['auth_type'],
            cc.auth_type,
        )
        self.assertEqual(
            defaults._defaults['identity_api_version'],
            cc.identity_api_version,
        )

    def test_get_one_auth_override_defaults(self):
        default_options = {'compute_api_version': '4'}
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   override_defaults=default_options)
        cc = c.get_one(cloud='_test-cloud_', auth={'username': 'user'})
        self.assertEqual('user', cc.auth['username'])
        self.assertEqual('4', cc.compute_api_version)
        self.assertEqual(
            defaults._defaults['identity_api_version'],
            cc.identity_api_version,
        )

    def test_get_one_with_config_files(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml],
                                   secure_files=[self.secure_yaml])
        self.assertIsInstance(c.cloud_config, dict)
        self.assertIn('cache', c.cloud_config)
        self.assertIsInstance(c.cloud_config['cache'], dict)
        self.assertIn('max_age', c.cloud_config['cache'])
        self.assertIn('path', c.cloud_config['cache'])
        cc = c.get_one('_test-cloud_')
        self._assert_cloud_details(cc)
        cc = c.get_one('_test_cloud_no_vendor')
        self._assert_cloud_details(cc)

    def test_get_one_with_int_project_id(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        cc = c.get_one('_test-cloud-int-project_')
        self.assertEqual('12345', cc.auth['project_id'])

    def test_get_one_with_domain_id(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        cc = c.get_one('_test-cloud-domain-id_')
        self.assertEqual('6789', cc.auth['user_domain_id'])
        self.assertEqual('123456789', cc.auth['project_domain_id'])
        self.assertNotIn('domain_id', cc.auth)
        self.assertNotIn('domain-id', cc.auth)
        self.assertNotIn('domain_id', cc)

    def test_get_one_domain_scoped(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        cc = c.get_one('_test-cloud-domain-scoped_')
        self.assertEqual('12345', cc.auth['domain_id'])
        self.assertNotIn('user_domain_id', cc.auth)
        self.assertNotIn('project_domain_id', cc.auth)

    def test_get_one_infer_user_domain(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        cc = c.get_one('_test-cloud-int-project_')
        self.assertEqual('awesome-domain', cc.auth['user_domain_id'])
        self.assertEqual('awesome-domain', cc.auth['project_domain_id'])
        self.assertNotIn('domain_id', cc.auth)
        self.assertNotIn('domain_id', cc)

    def test_get_one_with_hyphenated_project_id(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        cc = c.get_one('_test_cloud_hyphenated')
        self.assertEqual('12345', cc.auth['project_id'])

    def test_get_one_with_hyphenated_kwargs(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        args = {
            'auth': {
                'username': 'testuser',
                'password': 'testpass',
                'project-id': '12345',
                'auth-url': 'http://example.com/v2',
            },
            'region_name': 'test-region',
        }
        cc = c.get_one(**args)
        self.assertEqual('http://example.com/v2', cc.auth['auth_url'])

    def test_no_environ(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        self.assertRaises(
            exceptions.ConfigException, c.get_one, 'envvars')

    def test_fallthrough(self):
        c = config.OpenStackConfig(config_files=[self.no_yaml],
                                   vendor_files=[self.no_yaml],
                                   secure_files=[self.no_yaml])
        for k in os.environ.keys():
            if k.startswith('OS_'):
                self.useFixture(fixtures.EnvironmentVariable(k))
        c.get_one(cloud='defaults', validate=False)

    def test_prefer_ipv6_true(self):
        c = config.OpenStackConfig(config_files=[self.no_yaml],
                                   vendor_files=[self.no_yaml],
                                   secure_files=[self.no_yaml])
        cc = c.get_one(cloud='defaults', validate=False)
        self.assertTrue(cc.prefer_ipv6)

    def test_prefer_ipv6_false(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        cc = c.get_one(cloud='_test-cloud_')
        self.assertFalse(cc.prefer_ipv6)

    def test_force_ipv4_true(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        cc = c.get_one(cloud='_test-cloud_')
        self.assertTrue(cc.force_ipv4)

    def test_force_ipv4_false(self):
        c = config.OpenStackConfig(config_files=[self.no_yaml],
                                   vendor_files=[self.no_yaml],
                                   secure_files=[self.no_yaml])
        cc = c.get_one(cloud='defaults', validate=False)
        self.assertFalse(cc.force_ipv4)

    def test_get_one_auth_merge(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml])
        cc = c.get_one(cloud='_test-cloud_', auth={'username': 'user'})
        self.assertEqual('user', cc.auth['username'])
        self.assertEqual('testpass', cc.auth['password'])

    def test_get_one_networks(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        cc = c.get_one('_test-cloud-networks_')
        self.assertEqual(
            ['a-public', 'another-public', 'split-default'],
            cc.get_external_networks())
        self.assertEqual(
            ['a-private', 'another-private', 'split-no-default'],
            cc.get_internal_networks())
        self.assertEqual('a-public', cc.get_nat_source())
        self.assertEqual('another-private', cc.get_nat_destination())
        self.assertEqual('another-public', cc.get_default_network())
        self.assertEqual(
            ['a-public', 'another-public', 'split-no-default'],
            cc.get_external_ipv4_networks())
        self.assertEqual(
            ['a-public', 'another-public', 'split-default'],
            cc.get_external_ipv6_networks())

    def test_get_one_no_networks(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        cc = c.get_one('_test-cloud-domain-scoped_')
        self.assertEqual([], cc.get_external_networks())
        self.assertEqual([], cc.get_internal_networks())
        self.assertIsNone(cc.get_nat_source())
        self.assertIsNone(cc.get_nat_destination())
        self.assertIsNone(cc.get_default_network())

    def test_only_secure_yaml(self):
        c = config.OpenStackConfig(config_files=['nonexistent'],
                                   vendor_files=['nonexistent'],
                                   secure_files=[self.secure_yaml])
        cc = c.get_one(cloud='_test_cloud_no_vendor', validate=False)
        self.assertEqual('testpass', cc.auth['password'])

    def test_get_cloud_names(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   secure_files=[self.no_yaml])
        self.assertEqual(
            ['_test-cloud-domain-id_',
             '_test-cloud-domain-scoped_',
             '_test-cloud-int-project_',
             '_test-cloud-networks_',
             '_test-cloud_',
             '_test-cloud_no_region',
             '_test_cloud_hyphenated',
             '_test_cloud_no_vendor',
             '_test_cloud_regions',
             ],
            sorted(c.get_cloud_names()))
        c = config.OpenStackConfig(config_files=[self.no_yaml],
                                   vendor_files=[self.no_yaml],
                                   secure_files=[self.no_yaml])
        for k in os.environ.keys():
            if k.startswith('OS_'):
                self.useFixture(fixtures.EnvironmentVariable(k))
        c.get_one(cloud='defaults', validate=False)
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
                'username': 'testuser',
                'auth_url': 'http://example.com/v2',
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
            # We write a cache config for testing
            written_config['cache'].pop('path', None)
            self.assertEqual(written_config, resulting_config)

    def test_get_region_no_region_default(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml],
                                   secure_files=[self.no_yaml])
        region = c._get_region(cloud='_test-cloud_no_region')
        self.assertEqual(region, {'name': '', 'values': {}})

    def test_get_region_no_region(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml],
                                   secure_files=[self.no_yaml])
        region = c._get_region(cloud='_test-cloud_no_region',
                               region_name='override-region')
        self.assertEqual(region, {'name': 'override-region', 'values': {}})

    def test_get_region_region_is_none(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml],
                                   secure_files=[self.no_yaml])
        region = c._get_region(cloud='_test-cloud_no_region', region_name=None)
        self.assertEqual(region, {'name': '', 'values': {}})

    def test_get_region_region_set(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml],
                                   secure_files=[self.no_yaml])
        region = c._get_region(cloud='_test-cloud_', region_name='test-region')
        self.assertEqual(region, {'name': 'test-region', 'values': {}})

    def test_get_region_many_regions_default(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml],
                                   secure_files=[self.no_yaml])
        region = c._get_region(cloud='_test_cloud_regions',
                               region_name='')
        self.assertEqual(region, {'name': 'region1', 'values':
                         {'external_network': 'region1-network'}})

    def test_get_region_many_regions(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml],
                                   secure_files=[self.no_yaml])
        region = c._get_region(cloud='_test_cloud_regions',
                               region_name='region2')
        self.assertEqual(region, {'name': 'region2', 'values':
                         {'external_network': 'my-network'}})

    def test_get_region_invalid_region(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml],
                                   secure_files=[self.no_yaml])
        self.assertRaises(
            exceptions.ConfigException, c._get_region,
            cloud='_test_cloud_regions', region_name='invalid-region')

    def test_get_region_no_cloud(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml],
                                   secure_files=[self.no_yaml])
        region = c._get_region(region_name='no-cloud-region')
        self.assertEqual(region, {'name': 'no-cloud-region', 'values': {}})


class TestExcludedFormattedConfigValue(base.TestCase):
    # verify https://storyboard.openstack.org/#!/story/1635696
    #
    # get_one_cloud() and get_one_cloud_osc() iterate over config
    # values and try to expand any variables in those values by
    # calling value.format(), however some config values
    # (e.g. password) should never have format() applied to them, not
    # only might that change the password but it will also cause the
    # format() function to raise an exception if it can not parse the
    # format string. Examples would be single brace (e.g. 'foo{')
    # which raises an ValueError because it's looking for a matching
    # end brace or a brace pair with a key value that cannot be found
    # (e.g. 'foo{bar}') which raises a KeyError.

    def setUp(self):
        super(TestExcludedFormattedConfigValue, self).setUp()

        self.args = dict(
            auth_url='http://example.com/v2',
            username='user',
            project_name='project',
            region_name='region2',
            snack_type='cookie',
            os_auth_token='no-good-things',
        )

        self.options = argparse.Namespace(**self.args)

    def test_get_one_cloud_password_brace(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])

        password = 'foo{'       # Would raise ValueError, single brace
        self.options.password = password
        cc = c.get_one_cloud(
            cloud='_test_cloud_regions', argparse=self.options, validate=False)
        self.assertEqual(cc.password, password)

        password = 'foo{bar}'   # Would raise KeyError, 'bar' not found
        self.options.password = password
        cc = c.get_one_cloud(
            cloud='_test_cloud_regions', argparse=self.options, validate=False)
        self.assertEqual(cc.password, password)

    def test_get_one_cloud_osc_password_brace(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        password = 'foo{'       # Would raise ValueError, single brace
        self.options.password = password
        cc = c.get_one_cloud_osc(
            cloud='_test_cloud_regions', argparse=self.options, validate=False)
        self.assertEqual(cc.password, password)

        password = 'foo{bar}'   # Would raise KeyError, 'bar' not found
        self.options.password = password
        cc = c.get_one_cloud_osc(
            cloud='_test_cloud_regions', argparse=self.options, validate=False)
        self.assertEqual(cc.password, password)


class TestConfigArgparse(base.TestCase):

    def setUp(self):
        super(TestConfigArgparse, self).setUp()

        self.args = dict(
            auth_url='http://example.com/v2',
            username='user',
            password='password',
            project_name='project',
            region_name='region2',
            snack_type='cookie',
            os_auth_token='no-good-things',
        )

        self.options = argparse.Namespace(**self.args)

    def test_get_one_bad_region_argparse(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])

        self.assertRaises(
            exceptions.ConfigException, c.get_one,
            cloud='_test-cloud_', argparse=self.options)

    def test_get_one_argparse(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])

        cc = c.get_one(
            cloud='_test_cloud_regions', argparse=self.options, validate=False)
        self.assertEqual(cc.region_name, 'region2')
        self.assertEqual(cc.snack_type, 'cookie')

    def test_get_one_precedence(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])

        kwargs = {
            'auth': {
                'username': 'testuser',
                'password': 'authpass',
                'project-id': 'testproject',
                'auth_url': 'http://example.com/v2',
            },
            'region_name': 'kwarg_region',
            'password': 'ansible_password',
            'arbitrary': 'value',
        }

        args = dict(
            auth_url='http://example.com/v2',
            username='user',
            password='argpass',
            project_name='project',
            region_name='region2',
            snack_type='cookie',
        )

        options = argparse.Namespace(**args)
        cc = c.get_one(
            argparse=options, **kwargs)
        self.assertEqual(cc.region_name, 'region2')
        self.assertEqual(cc.auth['password'], 'authpass')
        self.assertEqual(cc.snack_type, 'cookie')

    def test_get_one_cloud_precedence_osc(self):
        c = config.OpenStackConfig(
            config_files=[self.cloud_yaml],
            vendor_files=[self.vendor_yaml],
        )

        kwargs = {
            'auth': {
                'username': 'testuser',
                'password': 'authpass',
                'project-id': 'testproject',
                'auth_url': 'http://example.com/v2',
            },
            'region_name': 'kwarg_region',
            'password': 'ansible_password',
            'arbitrary': 'value',
        }

        args = dict(
            auth_url='http://example.com/v2',
            username='user',
            password='argpass',
            project_name='project',
            region_name='region2',
            snack_type='cookie',
        )

        options = argparse.Namespace(**args)
        cc = c.get_one_cloud_osc(
            argparse=options,
            **kwargs
        )
        self.assertEqual(cc.region_name, 'region2')
        self.assertEqual(cc.auth['password'], 'argpass')
        self.assertEqual(cc.snack_type, 'cookie')

    def test_get_one_precedence_no_argparse(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])

        kwargs = {
            'auth': {
                'username': 'testuser',
                'password': 'authpass',
                'project-id': 'testproject',
                'auth_url': 'http://example.com/v2',
            },
            'region_name': 'kwarg_region',
            'password': 'ansible_password',
            'arbitrary': 'value',
        }

        cc = c.get_one(**kwargs)
        self.assertEqual(cc.region_name, 'kwarg_region')
        self.assertEqual(cc.auth['password'], 'authpass')
        self.assertIsNone(cc.password)

    def test_get_one_just_argparse(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])

        cc = c.get_one(argparse=self.options, validate=False)
        self.assertIsNone(cc.cloud)
        self.assertEqual(cc.region_name, 'region2')
        self.assertEqual(cc.snack_type, 'cookie')

    def test_get_one_just_kwargs(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])

        cc = c.get_one(validate=False, **self.args)
        self.assertIsNone(cc.cloud)
        self.assertEqual(cc.region_name, 'region2')
        self.assertEqual(cc.snack_type, 'cookie')

    def test_get_one_dash_kwargs(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])

        args = {
            'auth-url': 'http://example.com/v2',
            'username': 'user',
            'password': 'password',
            'project_name': 'project',
            'region_name': 'other-test-region',
            'snack_type': 'cookie',
        }
        cc = c.get_one(**args)
        self.assertIsNone(cc.cloud)
        self.assertEqual(cc.region_name, 'other-test-region')
        self.assertEqual(cc.snack_type, 'cookie')

    def test_get_one_no_argparse(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])

        cc = c.get_one(cloud='_test-cloud_', argparse=None)
        self._assert_cloud_details(cc)
        self.assertEqual(cc.region_name, 'test-region')
        self.assertIsNone(cc.snack_type)

    def test_get_one_no_argparse_regions(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])

        cc = c.get_one(cloud='_test_cloud_regions', argparse=None)
        self._assert_cloud_details(cc)
        self.assertEqual(cc.region_name, 'region1')
        self.assertIsNone(cc.snack_type)

    def test_get_one_bad_region(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])

        self.assertRaises(
            exceptions.ConfigException,
            c.get_one,
            cloud='_test_cloud_regions', region_name='bad')

    def test_get_one_bad_region_no_regions(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        self.assertRaises(
            exceptions.ConfigException,
            c.get_one,
            cloud='_test-cloud_', region_name='bad_region')

    def test_get_one_no_argparse_region2(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])

        cc = c.get_one(
            cloud='_test_cloud_regions', region_name='region2', argparse=None)
        self._assert_cloud_details(cc)
        self.assertEqual(cc.region_name, 'region2')
        self.assertIsNone(cc.snack_type)

    def test_get_one_network(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])

        cc = c.get_one(
            cloud='_test_cloud_regions', region_name='region1', argparse=None)
        self._assert_cloud_details(cc)
        self.assertEqual(cc.region_name, 'region1')
        self.assertEqual('region1-network', cc.config['external_network'])

    def test_get_one_per_region_network(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])

        cc = c.get_one(
            cloud='_test_cloud_regions', region_name='region2', argparse=None)
        self._assert_cloud_details(cc)
        self.assertEqual(cc.region_name, 'region2')
        self.assertEqual('my-network', cc.config['external_network'])

    def test_get_one_no_yaml_no_cloud(self):
        c = config.OpenStackConfig(load_yaml_config=False)

        self.assertRaises(
            exceptions.ConfigException,
            c.get_one,
            cloud='_test_cloud_regions', region_name='region2', argparse=None)

    def test_get_one_no_yaml(self):
        c = config.OpenStackConfig(load_yaml_config=False)

        cc = c.get_one(
            region_name='region2', argparse=None,
            **base.USER_CONF['clouds']['_test_cloud_regions'])
        # Not using assert_cloud_details because of cache settings which
        # are not present without the file
        self.assertIsInstance(cc, cloud_region.CloudRegion)
        self.assertTrue(extras.safe_hasattr(cc, 'auth'))
        self.assertIsInstance(cc.auth, dict)
        self.assertIsNone(cc.cloud)
        self.assertIn('username', cc.auth)
        self.assertEqual('testuser', cc.auth['username'])
        self.assertEqual('testpass', cc.auth['password'])
        self.assertFalse(cc.config['image_api_use_tasks'])
        self.assertTrue('project_name' in cc.auth or 'project_id' in cc.auth)
        if 'project_name' in cc.auth:
            self.assertEqual('testproject', cc.auth['project_name'])
        elif 'project_id' in cc.auth:
            self.assertEqual('testproject', cc.auth['project_id'])
        self.assertEqual(cc.region_name, 'region2')

    def test_fix_env_args(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])

        env_args = {'os-compute-api-version': 1}
        fixed_args = c._fix_args(env_args)

        self.assertDictEqual({'compute_api_version': 1}, fixed_args)

    def test_extra_config(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])

        defaults = {'use_hostnames': False, 'other-value': 'something'}
        ansible_options = c.get_extra_config('ansible', defaults)

        # This should show that the default for use_hostnames above is
        # overridden by the value in the config file defined in base.py
        # It should also show that other-value key is normalized and passed
        # through even though there is no corresponding value in the config
        # file, and that expand-hostvars key is normalized and the value
        # from the config comes through even though there is no default.
        self.assertDictEqual(
            {
                'expand_hostvars': False,
                'use_hostnames': True,
                'other_value': 'something',
            },
            ansible_options)

    def test_get_client_config(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])

        cc = c.get_one(
            cloud='_test_cloud_regions')

        defaults = {
            'use_hostnames': False,
            'other-value': 'something',
            'force_ipv4': False,
        }
        ansible_options = cc.get_client_config('ansible', defaults)

        # This should show that the default for use_hostnames and force_ipv4
        # above is overridden by the value in the config file defined in
        # base.py
        # It should also show that other-value key is normalized and passed
        # through even though there is no corresponding value in the config
        # file, and that expand-hostvars key is normalized and the value
        # from the config comes through even though there is no default.
        self.assertDictEqual(
            {
                'expand_hostvars': False,
                'use_hostnames': True,
                'other_value': 'something',
                'force_ipv4': True,
            },
            ansible_options)

    def test_register_argparse_cloud(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        parser = argparse.ArgumentParser()
        c.register_argparse_arguments(parser, [])
        opts, _remain = parser.parse_known_args(['--os-cloud', 'foo'])
        self.assertEqual(opts.os_cloud, 'foo')

    def test_env_argparse_precedence(self):
        self.useFixture(fixtures.EnvironmentVariable(
            'OS_TENANT_NAME', 'tenants-are-bad'))
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])

        cc = c.get_one(
            cloud='envvars', argparse=self.options, validate=False)
        self.assertEqual(cc.auth['project_name'], 'project')

    def test_argparse_default_no_token(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])

        parser = argparse.ArgumentParser()
        c.register_argparse_arguments(parser, [])
        # novaclient will add this
        parser.add_argument('--os-auth-token')
        opts, _remain = parser.parse_known_args()
        cc = c.get_one(
            cloud='_test_cloud_regions', argparse=opts)
        self.assertEqual(cc.config['auth_type'], 'password')
        self.assertNotIn('token', cc.config['auth'])

    def test_argparse_token(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])

        parser = argparse.ArgumentParser()
        c.register_argparse_arguments(parser, [])
        # novaclient will add this
        parser.add_argument('--os-auth-token')
        opts, _remain = parser.parse_known_args(
            ['--os-auth-token', 'very-bad-things',
             '--os-auth-type', 'token'])
        cc = c.get_one(argparse=opts, validate=False)
        self.assertEqual(cc.config['auth_type'], 'token')
        self.assertEqual(cc.config['auth']['token'], 'very-bad-things')

    def test_argparse_underscores(self):
        c = config.OpenStackConfig(config_files=[self.no_yaml],
                                   vendor_files=[self.no_yaml],
                                   secure_files=[self.no_yaml])
        parser = argparse.ArgumentParser()
        parser.add_argument('--os_username')
        argv = [
            '--os_username', 'user', '--os_password', 'pass',
            '--os-auth-url', 'auth-url', '--os-project-name', 'project']
        c.register_argparse_arguments(parser, argv=argv)
        opts, _remain = parser.parse_known_args(argv)
        cc = c.get_one(argparse=opts)
        self.assertEqual(cc.config['auth']['username'], 'user')
        self.assertEqual(cc.config['auth']['password'], 'pass')
        self.assertEqual(cc.config['auth']['auth_url'], 'auth-url')

    def test_argparse_action_append_no_underscore(self):
        c = config.OpenStackConfig(config_files=[self.no_yaml],
                                   vendor_files=[self.no_yaml],
                                   secure_files=[self.no_yaml])
        parser = argparse.ArgumentParser()
        parser.add_argument('--foo', action='append')
        argv = ['--foo', '1', '--foo', '2']
        c.register_argparse_arguments(parser, argv=argv)
        opts, _remain = parser.parse_known_args(argv)
        self.assertEqual(opts.foo, ['1', '2'])

    def test_argparse_underscores_duplicate(self):
        c = config.OpenStackConfig(config_files=[self.no_yaml],
                                   vendor_files=[self.no_yaml],
                                   secure_files=[self.no_yaml])
        parser = argparse.ArgumentParser()
        parser.add_argument('--os_username')
        argv = [
            '--os_username', 'user', '--os_password', 'pass',
            '--os-username', 'user1', '--os-password', 'pass1',
            '--os-auth-url', 'auth-url', '--os-project-name', 'project']
        self.assertRaises(
            exceptions.ConfigException,
            c.register_argparse_arguments,
            parser=parser, argv=argv)

    def test_register_argparse_bad_plugin(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        parser = argparse.ArgumentParser()
        self.assertRaises(
            exceptions.ConfigException,
            c.register_argparse_arguments,
            parser, ['--os-auth-type', 'foo'])

    def test_register_argparse_not_password(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        parser = argparse.ArgumentParser()
        args = [
            '--os-auth-type', 'v3token',
            '--os-token', 'some-secret',
        ]
        c.register_argparse_arguments(parser, args)
        opts, _remain = parser.parse_known_args(args)
        self.assertEqual(opts.os_token, 'some-secret')

    def test_register_argparse_password(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        parser = argparse.ArgumentParser()
        args = [
            '--os-password', 'some-secret',
        ]
        c.register_argparse_arguments(parser, args)
        opts, _remain = parser.parse_known_args(args)
        self.assertEqual(opts.os_password, 'some-secret')
        with testtools.ExpectedException(AttributeError):
            opts.os_token

    def test_register_argparse_service_type(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        parser = argparse.ArgumentParser()
        args = [
            '--os-service-type', 'network',
            '--os-endpoint-type', 'admin',
            '--http-timeout', '20',
        ]
        c.register_argparse_arguments(parser, args)
        opts, _remain = parser.parse_known_args(args)
        self.assertEqual(opts.os_service_type, 'network')
        self.assertEqual(opts.os_endpoint_type, 'admin')
        self.assertEqual(opts.http_timeout, '20')
        with testtools.ExpectedException(AttributeError):
            opts.os_network_service_type
        cloud = c.get_one(argparse=opts, validate=False)
        self.assertEqual(cloud.config['service_type'], 'network')
        self.assertEqual(cloud.config['interface'], 'admin')
        self.assertEqual(cloud.config['api_timeout'], '20')
        self.assertNotIn('http_timeout', cloud.config)

    def test_register_argparse_network_service_type(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        parser = argparse.ArgumentParser()
        args = [
            '--os-endpoint-type', 'admin',
            '--network-api-version', '4',
        ]
        c.register_argparse_arguments(parser, args, ['network'])
        opts, _remain = parser.parse_known_args(args)
        self.assertEqual(opts.os_service_type, 'network')
        self.assertEqual(opts.os_endpoint_type, 'admin')
        self.assertIsNone(opts.os_network_service_type)
        self.assertIsNone(opts.os_network_api_version)
        self.assertEqual(opts.network_api_version, '4')
        cloud = c.get_one(argparse=opts, validate=False)
        self.assertEqual(cloud.config['service_type'], 'network')
        self.assertEqual(cloud.config['interface'], 'admin')
        self.assertEqual(cloud.config['network_api_version'], '4')
        self.assertNotIn('http_timeout', cloud.config)

    def test_register_argparse_network_service_types(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        parser = argparse.ArgumentParser()
        args = [
            '--os-compute-service-name', 'cloudServers',
            '--os-network-service-type', 'badtype',
            '--os-endpoint-type', 'admin',
            '--network-api-version', '4',
        ]
        c.register_argparse_arguments(
            parser, args, ['compute', 'network', 'volume'])
        opts, _remain = parser.parse_known_args(args)
        self.assertEqual(opts.os_network_service_type, 'badtype')
        self.assertIsNone(opts.os_compute_service_type)
        self.assertIsNone(opts.os_volume_service_type)
        self.assertEqual(opts.os_service_type, 'compute')
        self.assertEqual(opts.os_compute_service_name, 'cloudServers')
        self.assertEqual(opts.os_endpoint_type, 'admin')
        self.assertIsNone(opts.os_network_api_version)
        self.assertEqual(opts.network_api_version, '4')
        cloud = c.get_one(argparse=opts, validate=False)
        self.assertEqual(cloud.config['service_type'], 'compute')
        self.assertEqual(cloud.config['network_service_type'], 'badtype')
        self.assertEqual(cloud.config['interface'], 'admin')
        self.assertEqual(cloud.config['network_api_version'], '4')
        self.assertNotIn('volume_service_type', cloud.config)
        self.assertNotIn('http_timeout', cloud.config)


class TestConfigPrompt(base.TestCase):

    def setUp(self):
        super(TestConfigPrompt, self).setUp()

        self.args = dict(
            auth_url='http://example.com/v2',
            username='user',
            project_name='project',
            # region_name='region2',
            auth_type='password',
        )

        self.options = argparse.Namespace(**self.args)

    def test_get_one_prompt(self):
        c = config.OpenStackConfig(
            config_files=[self.cloud_yaml],
            vendor_files=[self.vendor_yaml],
            pw_func=prompt_for_password,
        )

        # This needs a cloud definition without a password.
        # If this starts failing unexpectedly check that the cloud_yaml
        # and/or vendor_yaml do not have a password in the selected cloud.
        cc = c.get_one(
            cloud='_test_cloud_no_vendor',
            argparse=self.options,
        )
        self.assertEqual('promptpass', cc.auth['password'])


class TestConfigDefault(base.TestCase):

    def setUp(self):
        super(TestConfigDefault, self).setUp()

        # Reset defaults after each test so that other tests are
        # not affected by any changes.
        self.addCleanup(self._reset_defaults)

    def _reset_defaults(self):
        defaults._defaults = None

    def test_set_no_default(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        cc = c.get_one(cloud='_test-cloud_', argparse=None)
        self._assert_cloud_details(cc)
        self.assertEqual('password', cc.auth_type)


class TestBackwardsCompatibility(base.TestCase):

    def test_set_no_default(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        cloud = {
            'identity_endpoint_type': 'admin',
            'compute_endpoint_type': 'private',
            'endpoint_type': 'public',
            'auth_type': 'v3password',
        }
        result = c._fix_backwards_interface(cloud)
        expected = {
            'identity_interface': 'admin',
            'compute_interface': 'private',
            'interface': 'public',
            'auth_type': 'v3password',
        }
        self.assertDictEqual(expected, result)

    def test_project_v2password(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        cloud = {
            'auth_type': 'v2password',
            'auth': {
                'project-name': 'my_project_name',
                'project-id': 'my_project_id'
            }
        }
        result = c._fix_backwards_project(cloud)
        expected = {
            'auth_type': 'v2password',
            'auth': {
                'tenant_name': 'my_project_name',
                'tenant_id': 'my_project_id'
            }
        }
        self.assertEqual(expected, result)

    def test_project_password(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        cloud = {
            'auth_type': 'password',
            'auth': {
                'project-name': 'my_project_name',
                'project-id': 'my_project_id'
            }
        }
        result = c._fix_backwards_project(cloud)
        expected = {
            'auth_type': 'password',
            'auth': {
                'project_name': 'my_project_name',
                'project_id': 'my_project_id'
            }
        }
        self.assertEqual(expected, result)

    def test_backwards_network_fail(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        cloud = {
            'external_network': 'public',
            'networks': [
                {'name': 'private', 'routes_externally': False},
            ]
        }
        self.assertRaises(
            exceptions.ConfigException,
            c._fix_backwards_networks, cloud)

    def test_backwards_network(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        cloud = {
            'external_network': 'public',
            'internal_network': 'private',
        }
        result = c._fix_backwards_networks(cloud)
        expected = {
            'external_network': 'public',
            'internal_network': 'private',
            'networks': [
                {'name': 'public', 'routes_externally': True,
                 'nat_destination': False, 'default_interface': True},
                {'name': 'private', 'routes_externally': False,
                 'nat_destination': True, 'default_interface': False},
            ]
        }
        self.assertEqual(expected, result)

    def test_normalize_network(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        cloud = {
            'networks': [
                {'name': 'private'}
            ]
        }
        result = c._fix_backwards_networks(cloud)
        expected = {
            'networks': [
                {'name': 'private', 'routes_externally': False,
                 'nat_destination': False, 'default_interface': False,
                 'nat_source': False,
                 'routes_ipv4_externally': False,
                 'routes_ipv6_externally': False},
            ]
        }
        self.assertEqual(expected, result)

    def test_single_default_interface(self):
        c = config.OpenStackConfig(config_files=[self.cloud_yaml],
                                   vendor_files=[self.vendor_yaml])
        cloud = {
            'networks': [
                {'name': 'blue', 'default_interface': True},
                {'name': 'purple', 'default_interface': True},
            ]
        }
        self.assertRaises(
            exceptions.ConfigException,
            c._fix_backwards_networks, cloud)
