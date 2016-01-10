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

from keystoneauth1 import exceptions as _exceptions

from openstack.tests.functional import base


class TestServiceExists(unittest.TestCase):

    def setUp(self):
        super(TestServiceExists, self).setUp()

        self.conn = mock.Mock()
        self.sess = mock.Mock()
        self.conn.session = self.sess
        self.kwargs = {"service_type": "identity", "version": "v3"}

    @mock.patch('openstack.connection.from_config')
    def test_service_exists(self, mock_from_config):
        mock_from_config.return_value = self.conn

        self.sess.get_endpoint = mock.Mock()

        self.assertTrue(base.service_exists(**self.kwargs))

    @mock.patch('openstack.connection.from_config')
    def test_service_doesnt_exist(self, mock_from_config):
        mock_from_config.return_value = self.conn

        self.sess.get_endpoint = mock.Mock(
            side_effect=_exceptions.EndpointNotFound(''))

        self.assertFalse(base.service_exists(**self.kwargs))
