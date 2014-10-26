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

    def verify_create(self, mock_method, test_method):
        with mock.patch(mock_method) as mockList:
            expected = 'result'
            mockList.return_value = expected
            self.assertEqual(expected, test_method())
            mockList.assert_called_with(self.session)

    def verify_delete(self, mock_method, test_method):
        with mock.patch(mock_method) as mockFind:
            mockFind.return_value = None
            self.assertEqual(None, test_method())
            mockFind.assert_called_with(self.session)

    def verify_get(self, mock_method, test_method):
        with mock.patch(mock_method) as mockList:
            expected = 'result'
            mockList.return_value = expected
            self.assertEqual(expected, test_method())
            mockList.assert_called_with(self.session)

    def verify_find(self, mock_method, test_method):
        with mock.patch(mock_method) as mockFind:
            expected = 'result'
            name_or_id = 'name_or_id'
            mockFind.return_value = expected
            self.assertEqual(expected, test_method(name_or_id))
            mockFind.assert_called_with(self.session, name_or_id)

    def verify_list(self, mock_method, test_method):
        with mock.patch(mock_method) as mockList:
            expected = ['result']
            mockList.return_value = expected
            self.assertEqual(expected, test_method())
            mockList.assert_called_with(self.session)

    def verify_update(self, mock_method, test_method):
        with mock.patch(mock_method) as mockList:
            expected = 'result'
            mockList.return_value = expected
            self.assertEqual(expected, test_method())
            mockList.assert_called_with(self.session)
