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

    def _verify(self, mock_method, test_method,
                method_args=None, method_kwargs=None,
                expected_args=None, expected_kwargs=None,
                expected_result=None):
        with mock.patch(mock_method) as mocked:
            mocked.return_value = expected_result
            if any([method_args, method_kwargs]):
                method_args = method_args or ()
                method_kwargs = method_kwargs or {}
                expected_args = expected_args or ()
                expected_kwargs = expected_kwargs or {}

                self.assertEqual(expected_result, test_method(*method_args,
                                 **method_kwargs))
                mocked.assert_called_with(self.session,
                                          *expected_args, **expected_kwargs)
            else:
                self.assertEqual(expected_result, test_method())
                mocked.assert_called_with(self.session)

    def verify_create(self, mock_method, test_method, **kwargs):
        self._verify(mock_method, test_method, expected_result="result",
                     **kwargs)

    def verify_delete(self, mock_method, test_method, **kwargs):
        self._verify(mock_method, test_method, **kwargs)

    def verify_get(self, mock_method, test_method, **kwargs):
        self._verify(mock_method, test_method, expected_result="result",
                     **kwargs)

    def verify_find(self, mock_method, test_method, **kwargs):
        self._verify(mock_method, test_method, method_args=["name_or_id"],
                     expected_args=["name_or_id"], expected_result="result",
                     **kwargs)

    def verify_list(self, mock_method, test_method, **kwargs):
        self._verify(mock_method, test_method, expected_result=["result"],
                     **kwargs)

    def verify_update(self, mock_method, test_method, **kwargs):
        self._verify(mock_method, test_method, expected_result="result",
                     **kwargs)
