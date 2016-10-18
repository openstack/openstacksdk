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
import mock
import os
import os_client_config as occ
import tempfile

import shade.openstackcloud
from shade.tests import base


class BaseTestCase(base.TestCase):

    def setUp(self, cloud_config_fixture='clouds.yaml'):
        """Run before each test method to initialize test environment."""

        super(BaseTestCase, self).setUp()

        # Sleeps are for real testing, but unit tests shouldn't need them
        realsleep = time.sleep

        def _nosleep(seconds):
            return realsleep(seconds * 0.0001)

        self.sleep_fixture = self.useFixture(fixtures.MonkeyPatch(
                                             'time.sleep',
                                             _nosleep))
        self.fixtures_directory = 'shade/tests/unit/fixtures'

        # Isolate os-client-config from test environment
        config = tempfile.NamedTemporaryFile(delete=False)
        cloud_path = '%s/clouds/%s' % (self.fixtures_directory,
                                       cloud_config_fixture)
        with open(cloud_path, 'rb') as f:
            content = f.read()
            config.write(content)
        config.close()

        vendor = tempfile.NamedTemporaryFile(delete=False)
        vendor.write(b'{}')
        vendor.close()

        # set record mode depending on environment
        record_mode = os.environ.get('BETAMAX_RECORD_FIXTURES', False)
        if record_mode:
            self.record_fixtures = 'new_episodes'
        else:
            self.record_fixtures = None

        test_cloud = os.environ.get('SHADE_OS_CLOUD', '_test_cloud_')
        self.config = occ.OpenStackConfig(
            config_files=[config.name],
            vendor_files=[vendor.name],
            secure_files=['non-existant'])
        self.cloud_config = self.config.get_one_cloud(
            cloud=test_cloud, validate=False)
        self.cloud = shade.OpenStackCloud(
            cloud_config=self.cloud_config,
            log_inner_exceptions=True)
        self.strict_cloud = shade.OpenStackCloud(
            cloud_config=self.cloud_config,
            log_inner_exceptions=True,
            strict=True)
        self.op_cloud = shade.OperatorCloud(
            cloud_config=self.cloud_config,
            log_inner_exceptions=True)

        # Any unit tests using betamax directly need a ksa.Session with
        # an auth dict.
        self.full_cloud_config = self.config.get_one_cloud(
            cloud=test_cloud)
        self.full_cloud = shade.OpenStackCloud(
            cloud_config=self.full_cloud_config,
            log_inner_exceptions=True)
        self.full_op_cloud = shade.OperatorCloud(
            cloud_config=self.full_cloud_config,
            log_inner_exceptions=True)


class TestCase(BaseTestCase):

    def setUp(self, cloud_config_fixture='clouds.yaml'):

        super(TestCase, self).setUp(cloud_config_fixture=cloud_config_fixture)
        self.session_fixture = self.useFixture(fixtures.MonkeyPatch(
            'os_client_config.cloud_config.CloudConfig.get_session',
            mock.Mock()))
