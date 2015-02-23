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
import testtools

from openstack import utils


class Test_enable_logging(testtools.TestCase):

    def _console_tests(self, fake_logging, level, debug):
        the_logger = mock.MagicMock()
        fake_logging.getLogger.return_value = the_logger

        utils.enable_logging(debug=debug)

        self.assertEqual(the_logger.addHandler.call_count, 1)
        the_logger.setLevel.assert_called_with(level)

    def _file_tests(self, fake_logging, level, debug):
        the_logger = mock.MagicMock()
        fake_logging.getLogger.return_value = the_logger
        fake_path = "fake/path.log"

        utils.enable_logging(debug=debug, path=fake_path)

        fake_logging.FileHandler.assert_called_with(fake_path)
        self.assertEqual(the_logger.addHandler.call_count, 2)
        the_logger.setLevel.assert_called_with(level)

    @mock.patch("openstack.utils.logging")
    def test_debug_console(self, fake_logging):
        self._console_tests(fake_logging, fake_logging.DEBUG, True)

    @mock.patch("openstack.utils.logging")
    def test_warning_console(self, fake_logging):
        self._console_tests(fake_logging, fake_logging.WARNING, False)

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


class Test_CaseInsensitiveDict(testtools.TestCase):

    def test_create(self):
        sot1 = utils.CaseInsensitiveDict()
        self.assertEqual(sot1, {})

        d = {"hello": "hi"}
        sot2 = utils.CaseInsensitiveDict(d)
        self.assertEqual(sot2, d)

    def test_get_set(self):
        sot = utils.CaseInsensitiveDict()
        value = 100
        sot["LOL"] = value
        self.assertEqual(sot["lol"], value)
        self.assertIn("LOL", sot._dict)

        self.assertRaises(KeyError, sot.__setitem__, None, None)
        self.assertRaises(KeyError, sot.__getitem__, None)

    def test_del(self):
        sot = utils.CaseInsensitiveDict()
        value = 200
        sot["ROFL"] = value
        self.assertEqual(sot["rofl"], value)

        del sot["rOfL"]

        self.assertNotIn("ROFL", sot)

    def test_contains(self):
        sot = utils.CaseInsensitiveDict()
        sot["LMAO"] = 1

        self.assertIn("lMaO", sot)
        self.assertNotIn("lol", sot)

    def test_iter(self):
        parent = {"a": 1, "b": 2}
        sot = utils.CaseInsensitiveDict(parent)

        for key in sot:
            self.assertIn(key, parent)

    def test_len(self):
        parent = {"a": 1, "b": 2}
        sot = utils.CaseInsensitiveDict(parent)

        self.assertEqual(len(parent), len(sot))

    def test_repr(self):
        parent = {"a": 1, "b": 2}
        sot = utils.CaseInsensitiveDict(parent)

        self.assertEqual(repr(parent), repr(sot))

    def test_copy(self):
        parent = {"a": 1, "b": 2}
        sot = utils.CaseInsensitiveDict(parent)

        new = sot.copy()
        self.assertEqual(new, sot)
        self.assertIsNot(new, sot)
