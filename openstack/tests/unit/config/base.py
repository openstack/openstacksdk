# -*- coding: utf-8 -*-

# Copyright 2010-2011 OpenStack Foundation
# Copyright (c) 2013 Hewlett-Packard Development Company, L.P.
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

import copy
import os
import tempfile

import extras
import fixtures
import yaml

from openstack.config import cloud_region
from openstack.tests.unit import base

VENDOR_CONF = {
    'public-clouds': {
        '_test_cloud_in_our_cloud': {
            'auth': {
                'auth_url': 'http://example.com/v2',
                'username': 'testotheruser',
                'project_name': 'testproject',
            },
        },
    }
}
USER_CONF = {
    'cache': {
        'max_age': '1',
        'expiration': {
            'server': 5,
            'image': '7',
        },
    },
    'client': {
        'force_ipv4': True,
    },
    'clouds': {
        '_test-cloud_': {
            'profile': '_test_cloud_in_our_cloud',
            'auth': {
                'auth_url': 'http://example.com/v2',
                'username': 'testuser',
                'password': 'testpass',
            },
            'region_name': 'test-region',
        },
        '_test_cloud_no_vendor': {
            'profile': '_test_non_existant_cloud',
            'auth': {
                'auth_url': 'http://example.com/v2',
                'username': 'testuser',
                'project_name': 'testproject',
            },
            'region-name': 'test-region',
        },
        '_test-cloud-int-project_': {
            'auth': {
                'username': 'testuser',
                'password': 'testpass',
                'domain_id': 'awesome-domain',
                'project_id': 12345,
                'auth_url': 'http://example.com/v2',
            },
            'region_name': 'test-region',
        },
        '_test-cloud-domain-id_': {
            'auth': {
                'username': 'testuser',
                'password': 'testpass',
                'project_id': 12345,
                'auth_url': 'http://example.com/v2',
                'domain_id': '6789',
                'project_domain_id': '123456789',
            },
            'region_name': 'test-region',
        },
        '_test-cloud-networks_': {
            'auth': {
                'username': 'testuser',
                'password': 'testpass',
                'project_id': 12345,
                'auth_url': 'http://example.com/v2',
                'domain_id': '6789',
                'project_domain_id': '123456789',
            },
            'networks': [{
                'name': 'a-public',
                'routes_externally': True,
                'nat_source': True,
            }, {
                'name': 'another-public',
                'routes_externally': True,
                'default_interface': True,
            }, {
                'name': 'a-private',
                'routes_externally': False,
            }, {
                'name': 'another-private',
                'routes_externally': False,
                'nat_destination': True,
            }, {
                'name': 'split-default',
                'routes_externally': True,
                'routes_ipv4_externally': False,
            }, {
                'name': 'split-no-default',
                'routes_ipv6_externally': False,
                'routes_ipv4_externally': True,
            }],
            'region_name': 'test-region',
        },
        '_test_cloud_regions': {
            'auth': {
                'username': 'testuser',
                'password': 'testpass',
                'project-id': 'testproject',
                'auth_url': 'http://example.com/v2',
            },
            'regions': [
                {
                    'name': 'region1',
                    'values': {
                        'external_network': 'region1-network',
                    }
                },
                {
                    'name': 'region2',
                    'values': {
                        'external_network': 'my-network',
                    }
                }
            ],
        },
        '_test_cloud_hyphenated': {
            'auth': {
                'username': 'testuser',
                'password': 'testpass',
                'project-id': '12345',
                'auth_url': 'http://example.com/v2',
            },
            'region_name': 'test-region',
        },
        '_test-cloud_no_region': {
            'profile': '_test_cloud_in_our_cloud',
            'auth': {
                'auth_url': 'http://example.com/v2',
                'username': 'testuser',
                'password': 'testpass',
            },
        },
        '_test-cloud-domain-scoped_': {
            'auth': {
                'auth_url': 'http://example.com/v2',
                'username': 'testuser',
                'password': 'testpass',
                'domain-id': '12345',
            },
        },
    },
    'ansible': {
        'expand-hostvars': False,
        'use_hostnames': True,
    },
}
SECURE_CONF = {
    'clouds': {
        '_test_cloud_no_vendor': {
            'auth': {
                'password': 'testpass',
            },
        }
    }
}
NO_CONF = {
    'cache': {'max_age': 1},
}


def _write_yaml(obj):
    # Assume NestedTempfile so we don't have to cleanup
    with tempfile.NamedTemporaryFile(delete=False) as obj_yaml:
        obj_yaml.write(yaml.safe_dump(obj).encode('utf-8'))
        return obj_yaml.name


class TestCase(base.TestCase):
    """Test case base class for all unit tests."""

    def setUp(self):
        super(TestCase, self).setUp()

        conf = copy.deepcopy(USER_CONF)
        tdir = self.useFixture(fixtures.TempDir())
        conf['cache']['path'] = tdir.path
        self.cloud_yaml = _write_yaml(conf)
        self.secure_yaml = _write_yaml(SECURE_CONF)
        self.vendor_yaml = _write_yaml(VENDOR_CONF)
        self.no_yaml = _write_yaml(NO_CONF)

        # Isolate the test runs from the environment
        # Do this as two loops because you can't modify the dict in a loop
        # over the dict in 3.4
        keys_to_isolate = []
        for env in os.environ.keys():
            if env.startswith('OS_'):
                keys_to_isolate.append(env)
        for env in keys_to_isolate:
            self.useFixture(fixtures.EnvironmentVariable(env))

    def _assert_cloud_details(self, cc):
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
        self.assertEqual(cc.get_cache_expiration_time(), 1)
        self.assertEqual(cc.get_cache_resource_expiration('server'), 5.0)
        self.assertEqual(cc.get_cache_resource_expiration('image'), 7.0)
