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

from openstack.tests import base


class TestProxyBase(base.TestCase):
    def setUp(self):
        super(TestProxyBase, self).setUp()
        self.session = mock.MagicMock()

    def _verify(self, mock_method, test_method, method_args=None,
                expected=None):
        with mock.patch(mock_method) as mocked:
            mocked.return_value = expected
            if method_args is not None:
                self.assertEqual(expected, test_method(method_args))
                mocked.assert_called_with(self.session, method_args)
            else:
                self.assertEqual(expected, test_method())
                mocked.assert_called_with(self.session)

    def verify_create(self, mock_method, test_method):
        self._verify(mock_method, test_method, expected="result")

    def verify_delete(self, mock_method, test_method):
        self._verify(mock_method, test_method)

    def verify_get(self, mock_method, test_method):
        self._verify(mock_method, test_method, expected="result")

    def verify_find(self, mock_method, test_method):
        self._verify(mock_method, test_method, ["name_or_id"], "result")

    def verify_list(self, mock_method, test_method):
        self._verify(mock_method, test_method, expected=["result"])

    def verify_update(self, mock_method, test_method):
        self._verify(mock_method, test_method, expected="result")
