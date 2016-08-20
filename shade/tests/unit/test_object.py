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
from os_client_config import cloud_config
from swiftclient import service as swift_service
from swiftclient import exceptions as swift_exc
import testtools

import shade
import shade.openstackcloud
from shade import exc
from shade.tests.unit import base


class TestObject(base.TestCase):

    @mock.patch.object(cloud_config.CloudConfig, 'get_session')
    def test_swift_client_no_endpoint(self, get_session_mock):
        session_mock = mock.Mock()
        session_mock.get_endpoint.return_value = None
        get_session_mock.return_value = session_mock
        e = self.assertRaises(
            exc.OpenStackCloudException, lambda: self.cloud.swift_client)
        self.assertIn(
            'Failed to instantiate object-store client.', str(e))

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
        swift_mock.get_capabilities.return_value = {
            'swift': {'max_file_size': 1000},
            'slo': {'min_segment_size': 500}}
        self.assertEqual(500, self.cloud.get_object_segment_size(400))
        self.assertEqual(900, self.cloud.get_object_segment_size(900))
        self.assertEqual(1000, self.cloud.get_object_segment_size(1000))
        self.assertEqual(1000, self.cloud.get_object_segment_size(1100))

    @mock.patch.object(shade.OpenStackCloud, 'swift_client')
    def test_get_object_segment_size_http_412(self, swift_mock):
        swift_mock.get_capabilities.side_effect = swift_exc.ClientException(
            "Precondition failed", http_status=412)
        self.assertEqual(shade.openstackcloud.DEFAULT_OBJECT_SEGMENT_SIZE,
                         self.cloud.get_object_segment_size(None))

    @mock.patch.object(shade.OpenStackCloud, 'swift_client')
    def test_create_container(self, mock_swift):
        """Test creating a (private) container"""
        name = 'test_container'
        mock_swift.head_container.return_value = None

        self.cloud.create_container(name)

        expected_head_container_calls = [
            # once for exist test
            mock.call(container=name),
            # once for the final return
            mock.call(container=name, skip_cache=True)
        ]
        self.assertTrue(expected_head_container_calls,
                        mock_swift.head_container.call_args_list)
        mock_swift.put_container.assert_called_once_with(container=name)
        # Because the default is 'private', we shouldn't be calling update
        self.assertFalse(mock_swift.post_container.called)

    @mock.patch.object(shade.OpenStackCloud, 'swift_client')
    def test_create_container_public(self, mock_swift):
        """Test creating a public container"""
        name = 'test_container'
        mock_swift.head_container.return_value = None

        self.cloud.create_container(name, public=True)

        expected_head_container_calls = [
            # once for exist test
            mock.call(container=name),
            # once for the final return
            mock.call(container=name, skip_cache=True)
        ]
        self.assertTrue(expected_head_container_calls,
                        mock_swift.head_container.call_args_list)
        mock_swift.put_container.assert_called_once_with(container=name)
        mock_swift.post_container.assert_called_once_with(
            container=name,
            headers={'x-container-read':
                     shade.openstackcloud.OBJECT_CONTAINER_ACLS['public']}
        )

    @mock.patch.object(shade.OpenStackCloud, 'swift_client')
    def test_create_container_exists(self, mock_swift):
        """Test creating a container that already exists"""
        name = 'test_container'
        fake_container = dict(id='1', name='name')
        mock_swift.head_container.return_value = fake_container
        container = self.cloud.create_container(name)
        mock_swift.head_container.assert_called_once_with(container=name)
        self.assertEqual(fake_container, container)

    @mock.patch.object(shade.OpenStackCloud, 'swift_client')
    def test_delete_container(self, mock_swift):
        name = 'test_container'
        self.cloud.delete_container(name)
        mock_swift.delete_container.assert_called_once_with(container=name)

    @mock.patch.object(shade.OpenStackCloud, 'swift_client')
    def test_delete_container_404(self, mock_swift):
        """No exception when deleting a container that does not exist"""
        name = 'test_container'
        mock_swift.delete_container.side_effect = swift_exc.ClientException(
            'ERROR', http_status=404)
        self.cloud.delete_container(name)
        mock_swift.delete_container.assert_called_once_with(container=name)

    @mock.patch.object(shade.OpenStackCloud, 'swift_client')
    def test_delete_container_error(self, mock_swift):
        """Non-404 swift error re-raised as OSCE"""
        mock_swift.delete_container.side_effect = swift_exc.ClientException(
            'ERROR')
        self.assertRaises(shade.OpenStackCloudException,
                          self.cloud.delete_container, '')

    @mock.patch.object(shade.OpenStackCloud, 'swift_client')
    def test_update_container(self, mock_swift):
        name = 'test_container'
        headers = {'x-container-read':
                   shade.openstackcloud.OBJECT_CONTAINER_ACLS['public']}
        self.cloud.update_container(name, headers)
        mock_swift.post_container.assert_called_once_with(
            container=name, headers=headers)

    @mock.patch.object(shade.OpenStackCloud, 'swift_client')
    def test_update_container_error(self, mock_swift):
        """Swift error re-raised as OSCE"""
        mock_swift.post_container.side_effect = swift_exc.ClientException(
            'ERROR')
        self.assertRaises(shade.OpenStackCloudException,
                          self.cloud.update_container, '', '')

    @mock.patch.object(shade.OpenStackCloud, 'swift_client')
    def test_set_container_access_public(self, mock_swift):
        name = 'test_container'
        self.cloud.set_container_access(name, 'public')
        mock_swift.post_container.assert_called_once_with(
            container=name,
            headers={'x-container-read':
                     shade.openstackcloud.OBJECT_CONTAINER_ACLS['public']})

    @mock.patch.object(shade.OpenStackCloud, 'swift_client')
    def test_set_container_access_private(self, mock_swift):
        name = 'test_container'
        self.cloud.set_container_access(name, 'private')
        mock_swift.post_container.assert_called_once_with(
            container=name,
            headers={'x-container-read':
                     shade.openstackcloud.OBJECT_CONTAINER_ACLS['private']})

    @mock.patch.object(shade.OpenStackCloud, 'swift_client')
    def test_set_container_access_invalid(self, mock_swift):
        self.assertRaises(shade.OpenStackCloudException,
                          self.cloud.set_container_access, '', 'invalid')

    @mock.patch.object(shade.OpenStackCloud, 'swift_client')
    def test_get_container(self, mock_swift):
        fake_container = {
            'x-container-read':
            shade.openstackcloud.OBJECT_CONTAINER_ACLS['public']
        }
        mock_swift.head_container.return_value = fake_container
        access = self.cloud.get_container_access('foo')
        self.assertEqual('public', access)

    @mock.patch.object(shade.OpenStackCloud, 'swift_client')
    def test_get_container_invalid(self, mock_swift):
        fake_container = {'x-container-read': 'invalid'}
        mock_swift.head_container.return_value = fake_container
        with testtools.ExpectedException(
                exc.OpenStackCloudException,
                "Could not determine container access for ACL: invalid"
        ):
            self.cloud.get_container_access('foo')

    @mock.patch.object(shade.OpenStackCloud, 'swift_client')
    def test_get_container_access_not_found(self, mock_swift):
        name = 'invalid_container'
        mock_swift.head_container.return_value = None
        with testtools.ExpectedException(
                exc.OpenStackCloudException,
                "Container not found: %s" % name
        ):
            self.cloud.get_container_access(name)

    @mock.patch.object(shade.OpenStackCloud, 'swift_client')
    def test_list_containers(self, mock_swift):
        containers = [dict(id='1', name='containter1')]
        mock_swift.get_account.return_value = ('response_headers', containers)
        ret = self.cloud.list_containers()
        mock_swift.get_account.assert_called_once_with(full_listing=True)
        self.assertEqual(containers, ret)

    @mock.patch.object(shade.OpenStackCloud, 'swift_client')
    def test_list_containers_not_full(self, mock_swift):
        containers = [dict(id='1', name='containter1')]
        mock_swift.get_account.return_value = ('response_headers', containers)
        ret = self.cloud.list_containers(full_listing=False)
        mock_swift.get_account.assert_called_once_with(full_listing=False)
        self.assertEqual(containers, ret)

    @mock.patch.object(shade.OpenStackCloud, 'swift_client')
    def test_list_containers_exception(self, mock_swift):
        mock_swift.get_account.side_effect = swift_exc.ClientException("ERROR")
        self.assertRaises(exc.OpenStackCloudException,
                          self.cloud.list_containers)

    @mock.patch.object(shade.OpenStackCloud, 'swift_client')
    def test_list_objects(self, mock_swift):
        objects = [dict(id='1', name='object1')]
        mock_swift.get_container.return_value = ('response_headers', objects)
        ret = self.cloud.list_objects('container_name')
        mock_swift.get_container.assert_called_once_with(
            container='container_name', full_listing=True)
        self.assertEqual(objects, ret)

    @mock.patch.object(shade.OpenStackCloud, 'swift_client')
    def test_list_objects_not_full(self, mock_swift):
        objects = [dict(id='1', name='object1')]
        mock_swift.get_container.return_value = ('response_headers', objects)
        ret = self.cloud.list_objects('container_name', full_listing=False)
        mock_swift.get_container.assert_called_once_with(
            container='container_name', full_listing=False)
        self.assertEqual(objects, ret)

    @mock.patch.object(shade.OpenStackCloud, 'swift_client')
    def test_list_objects_exception(self, mock_swift):
        mock_swift.get_container.side_effect = swift_exc.ClientException(
            "ERROR")
        self.assertRaises(exc.OpenStackCloudException,
                          self.cloud.list_objects, 'container_name')

    @mock.patch.object(shade.OpenStackCloud, 'get_object_metadata')
    @mock.patch.object(shade.OpenStackCloud, 'swift_client')
    def test_delete_object(self, mock_swift, mock_get_meta):
        container_name = 'container_name'
        object_name = 'object_name'
        mock_get_meta.return_value = {'object': object_name}
        self.assertTrue(self.cloud.delete_object(container_name, object_name))
        mock_get_meta.assert_called_once_with(container_name, object_name)
        mock_swift.delete_object.assert_called_once_with(
            container=container_name, obj=object_name
        )

    @mock.patch.object(shade.OpenStackCloud, 'get_object_metadata')
    @mock.patch.object(shade.OpenStackCloud, 'swift_client')
    def test_delete_object_not_found(self, mock_swift, mock_get_meta):
        container_name = 'container_name'
        object_name = 'object_name'
        mock_get_meta.return_value = None
        self.assertFalse(self.cloud.delete_object(container_name, object_name))
        mock_get_meta.assert_called_once_with(container_name, object_name)
        self.assertFalse(mock_swift.delete_object.called)

    @mock.patch.object(shade.OpenStackCloud, 'get_object_metadata')
    @mock.patch.object(shade.OpenStackCloud, 'swift_client')
    def test_delete_object_exception(self, mock_swift, mock_get_meta):
        container_name = 'container_name'
        object_name = 'object_name'
        mock_get_meta.return_value = {'object': object_name}
        mock_swift.delete_object.side_effect = swift_exc.ClientException(
            "ERROR")
        self.assertRaises(shade.OpenStackCloudException,
                          self.cloud.delete_object,
                          container_name, object_name)

    @mock.patch.object(shade.OpenStackCloud, 'swift_client')
    def test_get_object(self, mock_swift):
        fake_resp = ({'headers': 'yup'}, 'test body')
        mock_swift.get_object.return_value = fake_resp
        container_name = 'container_name'
        object_name = 'object_name'
        resp = self.cloud.get_object(container_name, object_name)
        self.assertEqual(fake_resp, resp)

    @mock.patch.object(shade.OpenStackCloud, 'swift_client')
    def test_get_object_not_found(self, mock_swift):
        mock_swift.get_object.side_effect = swift_exc.ClientException(
            'ERROR', http_status=404)
        container_name = 'container_name'
        object_name = 'object_name'
        self.assertIsNone(self.cloud.get_object(container_name, object_name))
        mock_swift.get_object.assert_called_once_with(
            container=container_name, obj=object_name,
            query_string=None, resp_chunk_size=None)

    @mock.patch.object(shade.OpenStackCloud, 'swift_client')
    def test_get_object_exception(self, mock_swift):
        mock_swift.get_object.side_effect = swift_exc.ClientException("ERROR")
        container_name = 'container_name'
        object_name = 'object_name'
        self.assertRaises(shade.OpenStackCloudException,
                          self.cloud.get_object,
                          container_name, object_name)
