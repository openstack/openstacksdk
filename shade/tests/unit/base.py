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

import time

import fixtures
import os_client_config as occ
import tempfile
import yaml

import shade.openstackcloud
from shade.tests import base


class TestCase(base.TestCase):

    """Test case base class for all unit tests."""

    CLOUD_CONFIG = {
        'clouds':
        {
            '_test_cloud_':
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
        """Run before each test method to initialize test environment."""

        super(TestCase, self).setUp()

        # Sleeps are for real testing, but unit tests shouldn't need them
        realsleep = time.sleep

        def _nosleep(seconds):
            return realsleep(seconds * 0.0001)

        self.sleep_fixture = self.useFixture(fixtures.MonkeyPatch(
                                             'time.sleep',
                                             _nosleep))

        # Isolate os-client-config from test environment
        config = tempfile.NamedTemporaryFile(delete=False)
        config.write(bytes(yaml.dump(self.CLOUD_CONFIG).encode('utf-8')))
        config.close()
        vendor = tempfile.NamedTemporaryFile(delete=False)
        vendor.write(b'{}')
        vendor.close()

        self.config = occ.OpenStackConfig(
            config_files=[config.name],
            vendor_files=[vendor.name])
        self.cloud_config = self.config.get_one_cloud(cloud='_test_cloud_')
        self.cloud = shade.OpenStackCloud(
            cloud_config=self.cloud_config,
            log_inner_exceptions=True)
