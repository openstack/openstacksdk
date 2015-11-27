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
import unittest

from openstack.tests.functional import base


class Test_requires_service(unittest.TestCase):

    def setUp(self):
        super(Test_requires_service, self).setUp()

        self.return_value = 1
        self.kwargs = {"service_type": "identity", "version": "v3"}

        self.sot = mock.Mock()
        self.sot.test_method = lambda *args: self.return_value

        self.mock_skip = mock.Mock()
        self.sot.skip = self.mock_skip

        self.get_endpoint = mock.Mock()
        self.sot.conn.session.get_endpoint = self.get_endpoint

    def _test(self, **kwargs):
        decorated = base.requires_service(**kwargs)(self.sot.test_method)
        return decorated(self.sot)

    def test_service_exists(self):
        self.assertEqual(self.return_value, self._test(**self.kwargs))
        self.get_endpoint.assert_called_with(**self.kwargs)

    def test_service_doesnt_exist(self):
        self.get_endpoint.return_value = None

        self._test(**self.kwargs)
        self.get_endpoint.assert_called_with(**self.kwargs)
        self.assertEqual(self.mock_skip.call_count, 1)
