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

import os
import sys

import fixtures
import logging
import munch
from oslotest import base
import pprint
from six import StringIO
import testtools.content

_TRUE_VALUES = ('true', '1', 'yes')


class TestCase(base.BaseTestCase):

    """Test case base class for all tests."""

    # A way to adjust slow test classes
    TIMEOUT_SCALING_FACTOR = 1.0

    def setUp(self):
        """Run before each test method to initialize test environment."""
        # No openstacksdk unit tests should EVER run longer than a second.
        # Set this to 3 by default just to give us some fudge.
        # Do this before super setUp so that we intercept the default value
        # in oslotest. TODO(mordred) Make the default timeout configurable
        # in oslotest.
        self.useFixture(
            fixtures.EnvironmentVariable(
                'OS_TEST_TIMEOUT', os.environ.get('OS_TEST_TIMEOUT', '3')))

        super(TestCase, self).setUp()

        if os.environ.get('OS_LOG_CAPTURE') in _TRUE_VALUES:
            self._log_stream = StringIO()
            if os.environ.get('OS_ALWAYS_LOG') in _TRUE_VALUES:
                self.addCleanup(self.printLogs)
            else:
                self.addOnException(self.attachLogs)
        else:
            self._log_stream = sys.stdout

        handler = logging.StreamHandler(self._log_stream)
        formatter = logging.Formatter('%(asctime)s %(name)-32s %(message)s')
        handler.setFormatter(formatter)

        logger = logging.getLogger('openstack')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

        # Enable HTTP level tracing
        logger = logging.getLogger('keystoneauth')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        logger.propagate = False

    def _fake_logs(self):
        # Override _fake_logs in oslotest until we can get our
        # attach-on-exception logic added
        pass

    def assertEqual(self, first, second, *args, **kwargs):
        '''Munch aware wrapper'''
        if isinstance(first, munch.Munch):
            first = first.toDict()
        if isinstance(second, munch.Munch):
            second = second.toDict()
        return super(TestCase, self).assertEqual(
            first, second, *args, **kwargs)

    def printLogs(self, *args):
        self._log_stream.seek(0)
        print(self._log_stream.read())

    def attachLogs(self, *args):
        def reader():
            self._log_stream.seek(0)
            while True:
                x = self._log_stream.read(4096)
                if not x:
                    break
                yield x.encode('utf8')
        content = testtools.content.content_from_reader(
            reader,
            testtools.content_type.UTF8_TEXT,
            False)
        self.addDetail('logging', content)

    def add_info_on_exception(self, name, text):
        def add_content(unused):
            self.addDetail(name, testtools.content.text_content(
                pprint.pformat(text)))
        self.addOnException(add_content)
