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
from requests import structures
from requests_mock.contrib import fixture as rm_fixture
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


class TestCase(BaseTestCase):

    def setUp(self, cloud_config_fixture='clouds.yaml'):

        super(TestCase, self).setUp(cloud_config_fixture=cloud_config_fixture)
        self.session_fixture = self.useFixture(fixtures.MonkeyPatch(
            'os_client_config.cloud_config.CloudConfig.get_session',
            mock.Mock()))


class RequestsMockTestCase(BaseTestCase):

    def setUp(self, cloud_config_fixture='clouds.yaml'):

        super(RequestsMockTestCase, self).setUp(
            cloud_config_fixture=cloud_config_fixture)

        self._uri_registry = {}

        self.discovery_json = os.path.join(
            self.fixtures_directory, 'discovery.json')
        self.use_keystone_v3()

    def use_keystone_v3(self):
        self.adapter = self.useFixture(rm_fixture.Fixture())
        self.calls = []
        self.register_uri(
            'GET', 'http://192.168.0.19:35357/',
            text=open(self.discovery_json, 'r').read())
        self.register_uri(
            'POST', 'https://example.com/v3/auth/tokens',
            headers={
                'X-Subject-Token': self.getUniqueString()},
            text=open(
                os.path.join(
                    self.fixtures_directory,
                    'catalog-v3.json'),
                'r').read())
        self._make_test_cloud(identity_api_version='3')

    def use_keystone_v2(self):
        self.adapter = self.useFixture(rm_fixture.Fixture())
        self.calls = []
        self.register_uri(
            'GET', 'http://192.168.0.19:35357/',
            text=open(self.discovery_json, 'r').read())
        self.register_uri(
            'POST', 'https://example.com/v2.0/tokens',
            text=open(
                os.path.join(
                    self.fixtures_directory,
                    'catalog-v2.json'),
                'r').read())
        self._make_test_cloud(identity_api_version='2.0')

    def _make_test_cloud(self, **kwargs):
        test_cloud = os.environ.get('SHADE_OS_CLOUD', '_test_cloud_')
        self.cloud_config = self.config.get_one_cloud(
            cloud=test_cloud, validate=True, **kwargs)
        self.cloud = shade.OpenStackCloud(
            cloud_config=self.cloud_config,
            log_inner_exceptions=True)
        self.op_cloud = shade.OperatorCloud(
            cloud_config=self.cloud_config,
            log_inner_exceptions=True)

    def use_glance(self, image_version_json='image-version.json'):
        discovery_fixture = os.path.join(
            self.fixtures_directory, image_version_json)
        self.register_uri(
            'GET', 'https://image.example.com/',
            text=open(discovery_fixture, 'r').read())

    def register_uri(self, method, uri, **kwargs):
        validate = kwargs.pop('validate', {})
        key = '{method}:{uri}'.format(method=method, uri=uri)
        headers = structures.CaseInsensitiveDict(kwargs.pop('headers', {}))
        if 'content-type' not in headers:
            headers[u'content-type'] = 'application/json'
        kwargs['headers'] = headers

        if key in self._uri_registry:
            self._uri_registry[key].append(kwargs)
            self.adapter.register_uri(method, uri, self._uri_registry[key])
        else:
            self._uri_registry[key] = [kwargs]
            self.adapter.register_uri(method, uri, **kwargs)

        self.calls += [
            dict(
                method=method,
                url=uri, **validate)
        ]

    def assert_calls(self, stop_after=None):
        for (x, (call, history)) in enumerate(
                zip(self.calls, self.adapter.request_history)):
            if stop_after and x > stop_after:
                break
            self.assertEqual(
                call['method'], history.method,
                'Method mismatch on call {index}'.format(index=x))
            self.assertEqual(
                call['url'], history.url,
                'URL mismatch on call {index}'.format(index=x))
            if 'json' in call:
                self.assertEqual(
                    call['json'], history.json(),
                    'json content mismatch in call {index}'.format(index=x))
            # headers in a call isn't exhaustive - it's checking to make sure
            # a specific header or headers are there, not that they are the
            # only headers
            if 'headers' in call:
                for key, value in call['headers'].items():
                    self.assertEqual(
                        value, history.headers[key],
                        'header mismatch in call {index}'.format(index=x))
        self.assertEqual(len(self.calls), len(self.adapter.request_history))
