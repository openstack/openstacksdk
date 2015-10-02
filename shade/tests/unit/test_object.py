# -*- coding: utf-8 -*-
# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
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

import mock
import os_client_config
from swiftclient import client as swift_client
from swiftclient import service as swift_service
from swiftclient import exceptions as swift_exc

import shade
from shade import exc
from shade import OpenStackCloud
from shade.tests.unit import base


class TestObject(base.TestCase):

    def setUp(self):
        super(TestObject, self).setUp()
        config = os_client_config.OpenStackConfig()
        self.cloud = OpenStackCloud(
            cloud_config=config.get_one_cloud(validate=False))

    @mock.patch.object(swift_client, 'Connection')
    @mock.patch.object(shade.OpenStackCloud, 'keystone_session',
                       new_callable=mock.PropertyMock)
    @mock.patch.object(shade.OpenStackCloud, 'get_session_endpoint')
    def test_swift_client(self, endpoint_mock, session_mock, swift_mock):
        endpoint_mock.return_value = 'danzig'
        session = mock.MagicMock()
        session.get_token = mock.MagicMock()
        session.get_token.return_value = 'yankee'
        session_mock.return_value = session
        self.cloud.swift_client
        swift_mock.assert_called_with(
            preauthurl='danzig',
            preauthtoken='yankee',
            auth_version=mock.ANY,
            timeout=None,
            os_options=dict(
                object_storage_url='danzig',
                auth_token='yankee',
                region_name=''))

    @mock.patch.object(shade.OpenStackCloud, 'keystone_session',
                       new_callable=mock.PropertyMock)
    @mock.patch.object(shade.OpenStackCloud, 'get_session_endpoint')
    def test_swift_client_no_endpoint(self, endpoint_mock, session_mock):
        endpoint_mock.side_effect = KeyError
        e = self.assertRaises(
            exc.OpenStackCloudException, lambda: self.cloud.swift_client)
        self.assertIn(
            'Error constructing swift client', str(e))

    @mock.patch.object(shade.OpenStackCloud, 'auth_token')
    @mock.patch.object(shade.OpenStackCloud, 'get_session_endpoint')
    def test_swift_service(self, endpoint_mock, auth_mock):
        endpoint_mock.return_value = 'slayer'
        auth_mock.return_value = 'zulu'
        self.assertIsInstance(self.cloud.swift_service,
                              swift_service.SwiftService)
        endpoint_mock.assert_called_with(service_key='object-store')

    @mock.patch.object(shade.OpenStackCloud, 'get_session_endpoint')
    def test_swift_service_no_endpoint(self, endpoint_mock):
        endpoint_mock.side_effect = KeyError
        e = self.assertRaises(exc.OpenStackCloudException, lambda:
                              self.cloud.swift_service)
        self.assertIn(
            'Error constructing swift client', str(e))

    @mock.patch.object(shade.OpenStackCloud, 'swift_client')
    def test_get_object_segment_size(self, swift_mock):
        swift_mock.get_capabilities.return_value = {'swift':
                                                    {'max_file_size': 1000}}
        self.assertEqual(900, self.cloud.get_object_segment_size(900))
        self.assertEqual(1000, self.cloud.get_object_segment_size(1000))
        self.assertEqual(1000, self.cloud.get_object_segment_size(1100))

    @mock.patch.object(shade.OpenStackCloud, 'swift_client')
    def test_get_object_segment_size_http_412(self, swift_mock):
        swift_mock.get_capabilities.side_effect = swift_exc.ClientException(
            "Precondition failed", http_status=412)
        self.assertEqual(shade.DEFAULT_OBJECT_SEGMENT_SIZE,
                         self.cloud.get_object_segment_size(None))
