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

import concurrent.futures
import logging
import sys
from unittest import mock

import fixtures
import os_service_types
import testtools

import openstack
from openstack import exceptions
from openstack.tests.unit import base
from openstack import utils


class Test_enable_logging(base.TestCase):
    def setUp(self):
        super().setUp()
        self.openstack_logger = mock.Mock()
        self.openstack_logger.handlers = []
        self.ksa_logger_root = mock.Mock()
        self.ksa_logger_root.handlers = []
        self.ksa_logger_1 = mock.Mock()
        self.ksa_logger_1.handlers = []
        self.ksa_logger_2 = mock.Mock()
        self.ksa_logger_2.handlers = []
        self.ksa_logger_3 = mock.Mock()
        self.ksa_logger_3.handlers = []
        self.urllib3_logger = mock.Mock()
        self.urllib3_logger.handlers = []
        self.stevedore_logger = mock.Mock()
        self.stevedore_logger.handlers = []
        self.fake_get_logger = mock.Mock()
        self.fake_get_logger.side_effect = [
            self.openstack_logger,
            self.ksa_logger_root,
            self.urllib3_logger,
            self.stevedore_logger,
            self.ksa_logger_1,
            self.ksa_logger_2,
            self.ksa_logger_3,
        ]
        self.useFixture(
            fixtures.MonkeyPatch('logging.getLogger', self.fake_get_logger)
        )

    def _console_tests(self, level, debug, stream):
        openstack.enable_logging(debug=debug, stream=stream)

        self.assertEqual(self.openstack_logger.addHandler.call_count, 1)
        self.openstack_logger.setLevel.assert_called_with(level)

    def _file_tests(self, level, debug):
        file_handler = mock.Mock()
        self.useFixture(
            fixtures.MonkeyPatch('logging.FileHandler', file_handler)
        )
        fake_path = "fake/path.log"

        openstack.enable_logging(debug=debug, path=fake_path)

        file_handler.assert_called_with(fake_path)
        self.assertEqual(self.openstack_logger.addHandler.call_count, 1)
        self.openstack_logger.setLevel.assert_called_with(level)

    def test_none(self):
        openstack.enable_logging(debug=True)
        self.fake_get_logger.assert_has_calls([])
        self.openstack_logger.setLevel.assert_called_with(logging.DEBUG)
        self.assertEqual(self.openstack_logger.addHandler.call_count, 1)
        self.assertIsInstance(
            self.openstack_logger.addHandler.call_args_list[0][0][0],
            logging.StreamHandler,
        )

    def test_debug_console_stderr(self):
        self._console_tests(logging.DEBUG, True, sys.stderr)

    def test_warning_console_stderr(self):
        self._console_tests(logging.INFO, False, sys.stderr)

    def test_debug_console_stdout(self):
        self._console_tests(logging.DEBUG, True, sys.stdout)

    def test_warning_console_stdout(self):
        self._console_tests(logging.INFO, False, sys.stdout)

    def test_debug_file(self):
        self._file_tests(logging.DEBUG, True)

    def test_warning_file(self):
        self._file_tests(logging.INFO, False)


class Test_urljoin(base.TestCase):
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

    def test_unicode_strings(self):
        root = "http://www.example.com"
        leaves = "ascii", "extra_chars-™"

        try:
            result = utils.urljoin(root, *leaves)
        except Exception:
            self.fail("urljoin failed on unicode strings")

        self.assertEqual(result, "http://www.example.com/ascii/extra_chars-™")


class TestSupportsMicroversion(base.TestCase):
    def setUp(self):
        super().setUp()
        self.adapter = mock.Mock(spec=['get_endpoint_data'])
        self.endpoint_data = mock.Mock(
            spec=['min_microversion', 'max_microversion'],
            min_microversion='1.1',
            max_microversion='1.99',
        )
        self.adapter.get_endpoint_data.return_value = self.endpoint_data

    def test_requested_supported_no_default(self):
        self.adapter.default_microversion = None
        self.assertTrue(utils.supports_microversion(self.adapter, '1.2'))

    def test_requested_not_supported_no_default(self):
        self.adapter.default_microversion = None
        self.assertFalse(utils.supports_microversion(self.adapter, '2.2'))

    def test_requested_not_supported_no_default_exception(self):
        self.adapter.default_microversion = None
        self.assertRaises(
            exceptions.SDKException,
            utils.supports_microversion,
            self.adapter,
            '2.2',
            True,
        )

    def test_requested_supported_higher_default(self):
        self.adapter.default_microversion = '1.8'
        self.assertTrue(utils.supports_microversion(self.adapter, '1.6'))

    def test_requested_supported_equal_default(self):
        self.adapter.default_microversion = '1.8'
        self.assertTrue(utils.supports_microversion(self.adapter, '1.8'))

    def test_requested_supported_lower_default(self):
        self.adapter.default_microversion = '1.2'
        self.assertFalse(utils.supports_microversion(self.adapter, '1.8'))

    def test_requested_supported_lower_default_exception(self):
        self.adapter.default_microversion = '1.2'
        self.assertRaises(
            exceptions.SDKException,
            utils.supports_microversion,
            self.adapter,
            '1.8',
            True,
        )

    @mock.patch('openstack.utils.supports_microversion')
    def test_require_microversion(self, sm_mock):
        utils.require_microversion(self.adapter, '1.2')
        sm_mock.assert_called_with(self.adapter, '1.2', raise_exception=True)


class TestMaximumSupportedMicroversion(base.TestCase):
    def setUp(self):
        super().setUp()
        self.adapter = mock.Mock(spec=['get_endpoint_data'])
        self.endpoint_data = mock.Mock(
            spec=['min_microversion', 'max_microversion'],
            min_microversion=None,
            max_microversion='1.99',
        )
        self.adapter.get_endpoint_data.return_value = self.endpoint_data

    def test_with_none(self):
        self.assertIsNone(
            utils.maximum_supported_microversion(self.adapter, None)
        )

    def test_with_value(self):
        self.assertEqual(
            '1.42', utils.maximum_supported_microversion(self.adapter, '1.42')
        )

    def test_value_more_than_max(self):
        self.assertEqual(
            '1.99', utils.maximum_supported_microversion(self.adapter, '1.100')
        )

    def test_value_less_than_min(self):
        self.endpoint_data.min_microversion = '1.42'
        self.assertIsNone(
            utils.maximum_supported_microversion(self.adapter, '1.2')
        )


class TestOsServiceTypesVersion(base.TestCase):
    def test_ost_version(self):
        ost_version = '2022-09-13T15:34:32.154125'
        self.assertEqual(
            ost_version,
            os_service_types.ServiceTypes().version,
            "This project must be pinned to the latest version of "
            "os-service-types. Please bump requirements.txt accordingly.",
        )


class TestTinyDAG(base.TestCase):
    test_graph = {
        'a': ['b', 'd', 'f'],
        'b': ['c', 'd'],
        'c': ['d'],
        'd': ['e'],
        'e': [],
        'f': ['e'],
        'g': ['e'],
    }

    @classmethod
    def _create_tinydag(cls, data):
        sot = utils.TinyDAG()
        for k, v in data.items():
            sot.add_node(k)
            for dep in v:
                sot.add_edge(k, dep)
        return sot

    def _verify_order(self, test_graph, test_list):
        for k, v in test_graph.items():
            for dep in v:
                self.assertTrue(test_list.index(k) < test_list.index(dep))

    def test_topological_sort(self):
        sot = self._create_tinydag(self.test_graph)
        sorted_list = sot.topological_sort()
        self._verify_order(sot.graph, sorted_list)
        self.assertEqual(len(self.test_graph.keys()), len(sorted_list))

    def test_walk(self):
        sot = self._create_tinydag(self.test_graph)
        sorted_list = []
        for node in sot.walk():
            sorted_list.append(node)
            sot.node_done(node)
        self._verify_order(sot.graph, sorted_list)
        self.assertEqual(len(self.test_graph.keys()), len(sorted_list))

    def test_walk_parallel(self):
        sot = self._create_tinydag(self.test_graph)
        sorted_list = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
            for node in sot.walk(timeout=1):
                executor.submit(test_walker_fn, sot, node, sorted_list)
        self._verify_order(sot.graph, sorted_list)
        self.assertEqual(len(self.test_graph.keys()), len(sorted_list))

    def test_walk_raise(self):
        sot = self._create_tinydag(self.test_graph)
        bad_node = 'f'
        with testtools.ExpectedException(exceptions.SDKException):
            for node in sot.walk(timeout=1):
                if node != bad_node:
                    sot.node_done(node)

    def test_add_node_after_edge(self):
        sot = utils.TinyDAG()
        sot.add_node('a')
        sot.add_edge('a', 'b')
        sot.add_node('a')
        self.assertEqual(sot._graph['a'], set('b'))


def test_walker_fn(graph, node, lst):
    lst.append(node)
    graph.node_done(node)
