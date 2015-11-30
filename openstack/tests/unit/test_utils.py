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

import mock
import sys
import testtools

from openstack import utils


class Test_enable_logging(testtools.TestCase):

    def _console_tests(self, fake_logging, level, debug, stream):
        the_logger = mock.Mock()
        fake_logging.getLogger.return_value = the_logger

        utils.enable_logging(debug=debug, stream=stream)

        self.assertEqual(the_logger.addHandler.call_count, 2)
        the_logger.setLevel.assert_called_with(level)

    def _file_tests(self, fake_logging, level, debug):
        the_logger = mock.Mock()
        fake_logging.getLogger.return_value = the_logger
        fake_path = "fake/path.log"

        utils.enable_logging(debug=debug, path=fake_path)

        fake_logging.FileHandler.assert_called_with(fake_path)
        self.assertEqual(the_logger.addHandler.call_count, 2)
        the_logger.setLevel.assert_called_with(level)

    def test_none(self):
        self.assertRaises(
            ValueError, utils.enable_logging,
            debug=True, path=None, stream=None)

    @mock.patch("openstack.utils.logging")
    def test_debug_console_stderr(self, fake_logging):
        self._console_tests(fake_logging,
                            fake_logging.DEBUG, True, sys.stderr)

    @mock.patch("openstack.utils.logging")
    def test_warning_console_stderr(self, fake_logging):
        self._console_tests(fake_logging,
                            fake_logging.WARNING, False, sys.stderr)

    @mock.patch("openstack.utils.logging")
    def test_debug_console_stdout(self, fake_logging):
        self._console_tests(fake_logging,
                            fake_logging.DEBUG, True, sys.stdout)

    @mock.patch("openstack.utils.logging")
    def test_warning_console_stdout(self, fake_logging):
        self._console_tests(fake_logging,
                            fake_logging.WARNING, False, sys.stdout)

    @mock.patch("openstack.utils.logging")
    def test_debug_file(self, fake_logging):
        self._file_tests(fake_logging, fake_logging.DEBUG, True)

    @mock.patch("openstack.utils.logging")
    def test_warning_file(self, fake_logging):
        self._file_tests(fake_logging, fake_logging.WARNING, False)


class Test_urljoin(testtools.TestCase):

    def test_strings(self):
        root = "http://www.example.com"
        leaves = "foo", "bar"

        result = utils.urljoin(root, *leaves)
        self.assertEqual(result, "http://www.example.com/foo/bar")

    def test_with_none(self):
        root = "http://www.example.com"
        leaves = "foo", None

        result = utils.urljoin(root, *leaves)
        self.assertEqual(result, "http://www.example.com/foo/")
