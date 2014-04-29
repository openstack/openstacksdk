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

import json
import os

import fixtures
import httpretty
import testtools

from openstack import utils

_TRUE_VALUES = ('true', '1', 'yes')


class TestCase(testtools.TestCase):

    """Test case base class for all unit tests."""

    def setUp(self):
        """Run before each test method to initialize test environment."""

        super(TestCase, self).setUp()
        test_timeout = os.environ.get('OS_TEST_TIMEOUT', 0)
        try:
            test_timeout = int(test_timeout)
        except ValueError:
            # If timeout value is invalid do not set a timeout.
            test_timeout = 0
        if test_timeout > 0:
            self.useFixture(fixtures.Timeout(test_timeout, gentle=True))

        self.useFixture(fixtures.NestedTempfile())
        self.useFixture(fixtures.TempHomeDir())

        if os.environ.get('OS_STDOUT_CAPTURE') in _TRUE_VALUES:
            stdout = self.useFixture(fixtures.StringStream('stdout')).stream
            self.useFixture(fixtures.MonkeyPatch('sys.stdout', stdout))
        if os.environ.get('OS_STDERR_CAPTURE') in _TRUE_VALUES:
            stderr = self.useFixture(fixtures.StringStream('stderr')).stream
            self.useFixture(fixtures.MonkeyPatch('sys.stderr', stderr))

        self.log_fixture = self.useFixture(fixtures.FakeLogger())


class TestTransportBase(TestCase):

    TEST_URL = 'http://www.root.url'

    def stub_url(self, method, path=None, base_url=None, **kwargs):
        if not base_url:
            base_url = self.TEST_URL

        if isinstance(path, (list, tuple)):
            base_url = utils.urljoin(base_url, *path)
        elif path:
            base_url = utils.urljoin(base_url, path)

        if 'json' in kwargs:
            json_data = kwargs.pop('json')
            if json_data is not None:
                kwargs['body'] = json.dumps(json_data)
                kwargs['Content-Type'] = 'application/json'

        httpretty.register_uri(method, base_url, **kwargs)

    def assertRequestHeaderEqual(self, name, val):
        """Verify that the last request made contains a header and its value

        The request must have already been made and httpretty must have been
        activated for the request.

        """
        headers = httpretty.last_request().headers
        self.assertEqual(val, headers.get(name))

    def assertResponseOK(self, resp, status=200, body=None):
        """Verify the Response object contains expected values

        Tests our defaults for a successful request.
        """

        self.assertTrue(resp.ok)
        self.assertEqual(status, resp.status_code)
        if body:
            self.assertEqual(body, resp.text)
