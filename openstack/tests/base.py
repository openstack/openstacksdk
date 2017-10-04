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

import fixtures
import logging
import munch
import pprint
from six import StringIO
import testtools
import testtools.content

_TRUE_VALUES = ('true', '1', 'yes')


class TestCase(testtools.TestCase):

    """Test case base class for all tests."""

    # A way to adjust slow test classes
    TIMEOUT_SCALING_FACTOR = 1.0

    def setUp(self):
        """Run before each test method to initialize test environment."""

        super(TestCase, self).setUp()
        test_timeout = int(os.environ.get('OS_TEST_TIMEOUT', 0))
        try:
            test_timeout = int(test_timeout * self.TIMEOUT_SCALING_FACTOR)
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

        self._log_stream = StringIO()
        if os.environ.get('OS_ALWAYS_LOG') in _TRUE_VALUES:
            self.addCleanup(self.printLogs)
        else:
            self.addOnException(self.attachLogs)

        handler = logging.StreamHandler(self._log_stream)
        formatter = logging.Formatter('%(asctime)s %(name)-32s %(message)s')
        handler.setFormatter(formatter)

        logger = logging.getLogger('shade')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

        # Enable HTTP level tracing
        logger = logging.getLogger('keystoneauth')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        logger.propagate = False

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
