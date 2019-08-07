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

import tempfile

import mock
import testtools

import openstack.cloud
import openstack.cloud.openstackcloud as oc_oc
from openstack.cloud import exc
from openstack import exceptions
from openstack.tests.unit import base
from openstack.object_store.v1 import _proxy


class BaseTestObject(base.TestCase):

    def setUp(self):
        super(BaseTestObject, self).setUp()

        self.container = self.getUniqueString()
        self.object = self.getUniqueString()
        self.endpoint = self.cloud._object_store_client.get_endpoint()
        self.container_endpoint = '{endpoint}/{container}'.format(
            endpoint=self.endpoint, container=self.container)
        self.object_endpoint = '{endpoint}/{object}'.format(
            endpoint=self.container_endpoint, object=self.object)


class TestObject(BaseTestObject):

    def test_create_container(self):
        """Test creating a (private) container"""
        self.register_uris([
            dict(method='HEAD', uri=self.container_endpoint, status_code=404),
            dict(method='PUT', uri=self.container_endpoint,
                 status_code=201,
                 headers={
                     'Date': 'Fri, 16 Dec 2016 18:21:20 GMT',
                     'Content-Length': '0',
                     'Content-Type': 'text/html; charset=UTF-8',
                 }),
            dict(method='HEAD', uri=self.container_endpoint,
                 headers={
                     'Content-Length': '0',
                     'X-Container-Object-Count': '0',
                     'Accept-Ranges': 'bytes',
                     'X-Storage-Policy': 'Policy-0',
                     'Date': 'Fri, 16 Dec 2016 18:29:05 GMT',
                     'X-Timestamp': '1481912480.41664',
                     'X-Trans-Id': 'tx60ec128d9dbf44b9add68-0058543271dfw1',
                     'X-Container-Bytes-Used': '0',
                     'Content-Type': 'text/plain; charset=utf-8'})
        ])

        self.cloud.create_container(self.container)
        self.assert_calls()

    def test_create_container_public(self):
        """Test creating a public container"""
        self.register_uris([
            dict(method='HEAD', uri=self.container_endpoint,
                 status_code=404),
            dict(method='PUT', uri=self.container_endpoint,
                 status_code=201,
                 headers={
                     'Date': 'Fri, 16 Dec 2016 18:21:20 GMT',
                     'Content-Length': '0',
                     'Content-Type': 'text/html; charset=UTF-8',
                 }),
            dict(method='POST', uri=self.container_endpoint,
                 status_code=201,
                 validate=dict(
                     headers={
                         'x-container-read':
                             oc_oc.OBJECT_CONTAINER_ACLS[
                                 'public']})),
            dict(method='HEAD', uri=self.container_endpoint,
                 headers={
                     'Content-Length': '0',
                     'X-Container-Object-Count': '0',
                     'Accept-Ranges': 'bytes',
                     'X-Storage-Policy': 'Policy-0',
                     'Date': 'Fri, 16 Dec 2016 18:29:05 GMT',
                     'X-Timestamp': '1481912480.41664',
                     'X-Trans-Id': 'tx60ec128d9dbf44b9add68-0058543271dfw1',
                     'X-Container-Bytes-Used': '0',
                     'Content-Type': 'text/plain; charset=utf-8'})
        ])

        self.cloud.create_container(self.container, public=True)
        self.assert_calls()

    def test_create_container_exists(self):
        """Test creating a container that exists."""
        self.register_uris([
            dict(method='HEAD', uri=self.container_endpoint,
                 headers={
                     'Content-Length': '0',
                     'X-Container-Object-Count': '0',
                     'Accept-Ranges': 'bytes',
                     'X-Storage-Policy': 'Policy-0',
                     'Date': 'Fri, 16 Dec 2016 18:29:05 GMT',
                     'X-Timestamp': '1481912480.41664',
                     'X-Trans-Id': 'tx60ec128d9dbf44b9add68-0058543271dfw1',
                     'X-Container-Bytes-Used': '0',
                     'Content-Type': 'text/plain; charset=utf-8'})
        ])

        container = self.cloud.create_container(self.container)

        self.assert_calls()
        self.assertIsNotNone(container)

    def test_delete_container(self):
        self.register_uris([
            dict(method='DELETE', uri=self.container_endpoint)])

        self.assertTrue(self.cloud.delete_container(self.container))
        self.assert_calls()

    def test_delete_container_404(self):
        """No exception when deleting a container that does not exist"""
        self.register_uris([
            dict(method='DELETE', uri=self.container_endpoint,
                 status_code=404)])

        self.assertFalse(self.cloud.delete_container(self.container))
        self.assert_calls()

    def test_delete_container_error(self):
        """Non-404 swift error re-raised as OSCE"""
        # 409 happens if the container is not empty
        self.register_uris([
            dict(method='DELETE', uri=self.container_endpoint,
                 status_code=409)])
        self.assertRaises(
            openstack.cloud.OpenStackCloudException,
            self.cloud.delete_container, self.container)
        self.assert_calls()

    def test_update_container(self):
        headers = {
            'x-container-read':
            oc_oc.OBJECT_CONTAINER_ACLS['public']}
        self.register_uris([
            dict(method='POST', uri=self.container_endpoint,
                 status_code=204,
                 validate=dict(headers=headers))])

        self.cloud.update_container(self.container, headers)
        self.assert_calls()

    def test_update_container_error(self):
        """Swift error re-raised as OSCE"""
        # This test is of questionable value - the swift API docs do not
        # declare error codes (other than 404 for the container) for this
        # method, and I cannot make a synthetic failure to validate a real
        # error code. So we're really just testing the shade adapter error
        # raising logic here, rather than anything specific to swift.
        self.register_uris([
            dict(method='POST', uri=self.container_endpoint,
                 status_code=409)])
        self.assertRaises(
            openstack.cloud.OpenStackCloudException,
            self.cloud.update_container, self.container, dict(foo='bar'))
        self.assert_calls()

    def test_set_container_access_public(self):
        self.register_uris([
            dict(method='POST', uri=self.container_endpoint,
                 status_code=204,
                 validate=dict(
                     headers={
                         'x-container-read':
                             oc_oc.OBJECT_CONTAINER_ACLS[
                                 'public']}))])

        self.cloud.set_container_access(self.container, 'public')

        self.assert_calls()

    def test_set_container_access_private(self):
        self.register_uris([
            dict(method='POST', uri=self.container_endpoint,
                 status_code=204,
                 validate=dict(
                     headers={
                         'x-container-read':
                             oc_oc.OBJECT_CONTAINER_ACLS[
                                 'private']}))])

        self.cloud.set_container_access(self.container, 'private')

        self.assert_calls()

    def test_set_container_access_invalid(self):
        self.assertRaises(
            openstack.cloud.OpenStackCloudException,
            self.cloud.set_container_access, self.container, 'invalid')

    def test_get_container_access(self):
        self.register_uris([
            dict(method='HEAD', uri=self.container_endpoint,
                 headers={
                     'x-container-read':
                         str(oc_oc.OBJECT_CONTAINER_ACLS[
                             'public'])})])
        access = self.cloud.get_container_access(self.container)
        self.assertEqual('public', access)

    def test_get_container_invalid(self):
        self.register_uris([
            dict(method='HEAD', uri=self.container_endpoint,
                 headers={'x-container-read': 'invalid'})])

        with testtools.ExpectedException(
                exc.OpenStackCloudException,
                "Could not determine container access for ACL: invalid"
        ):
            self.cloud.get_container_access(self.container)

    def test_get_container_access_not_found(self):
        self.register_uris([
            dict(method='HEAD', uri=self.container_endpoint,
                 status_code=404)])
        with testtools.ExpectedException(
                exc.OpenStackCloudException,
                "Container not found: %s" % self.container
        ):
            self.cloud.get_container_access(self.container)

    def test_list_containers(self):
        endpoint = '{endpoint}/?format=json'.format(
            endpoint=self.endpoint)
        containers = [
            {u'count': 0, u'bytes': 0, u'name': self.container}]

        self.register_uris([dict(method='GET', uri=endpoint, complete_qs=True,
                                 json=containers)])

        ret = self.cloud.list_containers()

        self.assert_calls()
        self.assertEqual(containers, ret)

    def test_list_containers_exception(self):
        endpoint = '{endpoint}/?format=json'.format(
            endpoint=self.endpoint)
        self.register_uris([dict(method='GET', uri=endpoint, complete_qs=True,
                                 status_code=416)])

        self.assertRaises(
            exc.OpenStackCloudException, self.cloud.list_containers)
        self.assert_calls()

    @mock.patch('time.time', autospec=True)
    def test_generate_form_signature_container_key(self, mock_time):

        mock_time.return_value = 12345

        self.register_uris([
            dict(method='HEAD', uri=self.container_endpoint,
                 headers={
                     'Content-Length': '0',
                     'X-Container-Object-Count': '0',
                     'Accept-Ranges': 'bytes',
                     'X-Storage-Policy': 'Policy-0',
                     'Date': 'Fri, 16 Dec 2016 18:29:05 GMT',
                     'X-Timestamp': '1481912480.41664',
                     'X-Trans-Id': 'tx60ec128d9dbf44b9add68-0058543271dfw1',
                     'X-Container-Bytes-Used': '0',
                     'X-Container-Meta-Temp-Url-Key': 'amazingly-secure-key',
                     'Content-Type': 'text/plain; charset=utf-8'})
        ])
        self.assertEqual(
            (13345, '60731fb66d46c97cdcb79b6154363179c500b9d9'),
            self.cloud.object_store.generate_form_signature(
                self.container,
                object_prefix='prefix/location',
                redirect_url='https://example.com/location',
                max_file_size=1024 * 1024 * 1024,
                max_upload_count=10, timeout=1000, temp_url_key=None))
        self.assert_calls()

    @mock.patch('time.time', autospec=True)
    def test_generate_form_signature_account_key(self, mock_time):

        mock_time.return_value = 12345

        self.register_uris([
            dict(method='HEAD', uri=self.container_endpoint,
                 headers={
                     'Content-Length': '0',
                     'X-Container-Object-Count': '0',
                     'Accept-Ranges': 'bytes',
                     'X-Storage-Policy': 'Policy-0',
                     'Date': 'Fri, 16 Dec 2016 18:29:05 GMT',
                     'X-Timestamp': '1481912480.41664',
                     'X-Trans-Id': 'tx60ec128d9dbf44b9add68-0058543271dfw1',
                     'X-Container-Bytes-Used': '0',
                     'Content-Type': 'text/plain; charset=utf-8'}),
            dict(method='HEAD', uri=self.endpoint + '/',
                 headers={
                     'X-Account-Meta-Temp-Url-Key': 'amazingly-secure-key'}),
        ])
        self.assertEqual(
            (13345, '3cb9bc83d5a4136421bb2c1f58b963740566646f'),
            self.cloud.object_store.generate_form_signature(
                self.container,
                object_prefix='prefix/location',
                redirect_url='https://example.com/location',
                max_file_size=1024 * 1024 * 1024,
                max_upload_count=10, timeout=1000, temp_url_key=None))
        self.assert_calls()

    @mock.patch('time.time')
    def test_generate_form_signature_key_argument(self, mock_time):

        mock_time.return_value = 12345

        self.assertEqual(
            (13345, '1c283a05c6628274b732212d9a885265e6f67b63'),
            self.cloud.object_store.generate_form_signature(
                self.container,
                object_prefix='prefix/location',
                redirect_url='https://example.com/location',
                max_file_size=1024 * 1024 * 1024,
                max_upload_count=10, timeout=1000,
                temp_url_key='amazingly-secure-key'))
        self.assert_calls()

    def test_generate_form_signature_no_key(self):

        self.register_uris([
            dict(method='HEAD', uri=self.container_endpoint,
                 headers={
                     'Content-Length': '0',
                     'X-Container-Object-Count': '0',
                     'Accept-Ranges': 'bytes',
                     'X-Storage-Policy': 'Policy-0',
                     'Date': 'Fri, 16 Dec 2016 18:29:05 GMT',
                     'X-Timestamp': '1481912480.41664',
                     'X-Trans-Id': 'tx60ec128d9dbf44b9add68-0058543271dfw1',
                     'X-Container-Bytes-Used': '0',
                     'Content-Type': 'text/plain; charset=utf-8'}),
            dict(method='HEAD', uri=self.endpoint + '/',
                 headers={}),
        ])
        self.assertRaises(
            exceptions.SDKException,
            self.cloud.object_store.generate_form_signature,
            self.container,
            object_prefix='prefix/location',
            redirect_url='https://example.com/location',
            max_file_size=1024 * 1024 * 1024,
            max_upload_count=10, timeout=1000, temp_url_key=None)
        self.assert_calls()

    def test_set_account_temp_url_key(self):

        key = 'super-secure-key'

        self.register_uris([
            dict(method='POST', uri=self.endpoint + '/',
                 status_code=204,
                 validate=dict(
                     headers={
                         'x-account-meta-temp-url-key': key})),
            dict(method='HEAD', uri=self.endpoint + '/',
                 headers={
                     'x-account-meta-temp-url-key': key}),
        ])
        self.cloud.object_store.set_account_temp_url_key(key)
        self.assert_calls()

    def test_set_account_temp_url_key_secondary(self):

        key = 'super-secure-key'

        self.register_uris([
            dict(method='POST', uri=self.endpoint + '/',
                 status_code=204,
                 validate=dict(
                     headers={
                         'x-account-meta-temp-url-key-2': key})),
            dict(method='HEAD', uri=self.endpoint + '/',
                 headers={
                     'x-account-meta-temp-url-key-2': key}),
        ])
        self.cloud.object_store.set_account_temp_url_key(key, secondary=True)
        self.assert_calls()

    def test_set_container_temp_url_key(self):

        key = 'super-secure-key'

        self.register_uris([
            dict(method='POST', uri=self.container_endpoint,
                 status_code=204,
                 validate=dict(
                     headers={
                         'x-container-meta-temp-url-key': key})),
            dict(method='HEAD', uri=self.container_endpoint,
                 headers={
                     'x-container-meta-temp-url-key': key}),
        ])
        self.cloud.object_store.set_container_temp_url_key(self.container, key)
        self.assert_calls()

    def test_set_container_temp_url_key_secondary(self):

        key = 'super-secure-key'

        self.register_uris([
            dict(method='POST', uri=self.container_endpoint,
                 status_code=204,
                 validate=dict(
                     headers={
                         'x-container-meta-temp-url-key-2': key})),
            dict(method='HEAD', uri=self.container_endpoint,
                 headers={
                     'x-container-meta-temp-url-key-2': key}),
        ])
        self.cloud.object_store.set_container_temp_url_key(
            self.container, key, secondary=True)
        self.assert_calls()

    def test_list_objects(self):
        endpoint = '{endpoint}?format=json'.format(
            endpoint=self.container_endpoint)

        objects = [{
            u'bytes': 20304400896,
            u'last_modified': u'2016-12-15T13:34:13.650090',
            u'hash': u'daaf9ed2106d09bba96cf193d866445e',
            u'name': self.object,
            u'content_type': u'application/octet-stream'}]

        self.register_uris([dict(method='GET', uri=endpoint, complete_qs=True,
                                 json=objects)])

        ret = self.cloud.list_objects(self.container)

        self.assert_calls()
        self.assertEqual(objects, ret)

    def test_list_objects_with_prefix(self):
        endpoint = '{endpoint}?format=json&prefix=test'.format(
            endpoint=self.container_endpoint)

        objects = [{
            u'bytes': 20304400896,
            u'last_modified': u'2016-12-15T13:34:13.650090',
            u'hash': u'daaf9ed2106d09bba96cf193d866445e',
            u'name': self.object,
            u'content_type': u'application/octet-stream'}]

        self.register_uris([dict(method='GET', uri=endpoint, complete_qs=True,
                                 json=objects)])

        ret = self.cloud.list_objects(self.container, prefix='test')

        self.assert_calls()
        self.assertEqual(objects, ret)

    def test_list_objects_exception(self):
        endpoint = '{endpoint}?format=json'.format(
            endpoint=self.container_endpoint)
        self.register_uris([dict(method='GET', uri=endpoint, complete_qs=True,
                                 status_code=416)])
        self.assertRaises(
            exc.OpenStackCloudException,
            self.cloud.list_objects, self.container)
        self.assert_calls()

    def test_delete_object(self):
        self.register_uris([
            dict(method='HEAD', uri=self.object_endpoint,
                 headers={'X-Object-Meta': 'foo'}),
            dict(method='DELETE', uri=self.object_endpoint, status_code=204)])

        self.assertTrue(self.cloud.delete_object(self.container, self.object))

        self.assert_calls()

    def test_delete_object_not_found(self):
        self.register_uris([dict(method='HEAD', uri=self.object_endpoint,
                                 status_code=404)])

        self.assertFalse(self.cloud.delete_object(self.container, self.object))

        self.assert_calls()

    def test_get_object(self):
        headers = {
            'Content-Length': '20304400896',
            'Content-Type': 'application/octet-stream',
            'Accept-Ranges': 'bytes',
            'Last-Modified': 'Thu, 15 Dec 2016 13:34:14 GMT',
            'Etag': '"b5c454b44fbd5344793e3fb7e3850768"',
            'X-Timestamp': '1481808853.65009',
            'X-Trans-Id': 'tx68c2a2278f0c469bb6de1-005857ed80dfw1',
            'Date': 'Mon, 19 Dec 2016 14:24:00 GMT',
            'X-Static-Large-Object': 'True',
            'X-Object-Meta-Mtime': '1481513709.168512',
        }
        response_headers = {k.lower(): v for k, v in headers.items()}
        text = 'test body'
        self.register_uris([
            dict(method='GET', uri=self.object_endpoint,
                 headers={
                     'Content-Length': '20304400896',
                     'Content-Type': 'application/octet-stream',
                     'Accept-Ranges': 'bytes',
                     'Last-Modified': 'Thu, 15 Dec 2016 13:34:14 GMT',
                     'Etag': '"b5c454b44fbd5344793e3fb7e3850768"',
                     'X-Timestamp': '1481808853.65009',
                     'X-Trans-Id': 'tx68c2a2278f0c469bb6de1-005857ed80dfw1',
                     'Date': 'Mon, 19 Dec 2016 14:24:00 GMT',
                     'X-Static-Large-Object': 'True',
                     'X-Object-Meta-Mtime': '1481513709.168512',
                 },
                 text='test body')])

        resp = self.cloud.get_object(self.container, self.object)

        self.assert_calls()

        self.assertEqual((response_headers, text), resp)

    def test_stream_object(self):
        text = b'test body'
        self.register_uris([
            dict(method='GET', uri=self.object_endpoint,
                 headers={
                     'Content-Length': '20304400896',
                     'Content-Type': 'application/octet-stream',
                     'Accept-Ranges': 'bytes',
                     'Last-Modified': 'Thu, 15 Dec 2016 13:34:14 GMT',
                     'Etag': '"b5c454b44fbd5344793e3fb7e3850768"',
                     'X-Timestamp': '1481808853.65009',
                     'X-Trans-Id': 'tx68c2a2278f0c469bb6de1-005857ed80dfw1',
                     'Date': 'Mon, 19 Dec 2016 14:24:00 GMT',
                     'X-Static-Large-Object': 'True',
                     'X-Object-Meta-Mtime': '1481513709.168512',
                 },
                 text='test body')])

        response_text = b''
        for data in self.cloud.stream_object(self.container, self.object):
            response_text += data

        self.assert_calls()

        self.assertEqual(text, response_text)

    def test_stream_object_not_found(self):
        self.register_uris([
            dict(method='GET', uri=self.object_endpoint, status_code=404),
        ])

        response_text = b''
        for data in self.cloud.stream_object(self.container, self.object):
            response_text += data

        self.assert_calls()

        self.assertEqual(b'', response_text)

    def test_get_object_not_found(self):
        self.register_uris([dict(method='GET',
                                 uri=self.object_endpoint, status_code=404)])

        self.assertIsNone(self.cloud.get_object(self.container, self.object))

        self.assert_calls()

    def test_get_object_exception(self):
        self.register_uris([dict(method='GET', uri=self.object_endpoint,
                                 status_code=416)])

        self.assertRaises(
            openstack.cloud.OpenStackCloudException,
            self.cloud.get_object,
            self.container, self.object)

        self.assert_calls()

    def test_get_object_segment_size_below_min(self):
        # Register directly becuase we make multiple calls. The number
        # of calls we make isn't interesting - what we do with the return
        # values is. Don't run assert_calls for the same reason.
        self.register_uris([
            dict(method='GET', uri='https://object-store.example.com/info',
                 json=dict(
                     swift={'max_file_size': 1000},
                     slo={'min_segment_size': 500}),
                 headers={'Content-Type': 'application/json'})])
        self.assertEqual(500, self.cloud.get_object_segment_size(400))
        self.assertEqual(900, self.cloud.get_object_segment_size(900))
        self.assertEqual(1000, self.cloud.get_object_segment_size(1000))
        self.assertEqual(1000, self.cloud.get_object_segment_size(1100))

    def test_get_object_segment_size_http_404(self):
        self.register_uris([
            dict(method='GET', uri='https://object-store.example.com/info',
                 status_code=404, reason='Not Found')])
        self.assertEqual(_proxy.DEFAULT_OBJECT_SEGMENT_SIZE,
                         self.cloud.get_object_segment_size(None))
        self.assert_calls()

    def test_get_object_segment_size_http_412(self):
        self.register_uris([
            dict(method='GET', uri='https://object-store.example.com/info',
                 status_code=412, reason='Precondition failed')])
        self.assertEqual(
            _proxy.DEFAULT_OBJECT_SEGMENT_SIZE,
            self.cloud.get_object_segment_size(None))
        self.assert_calls()


class TestObjectUploads(BaseTestObject):

    def setUp(self):
        super(TestObjectUploads, self).setUp()

        self.content = self.getUniqueString().encode('latin-1')
        self.object_file = tempfile.NamedTemporaryFile(delete=False)
        self.object_file.write(self.content)
        self.object_file.close()
        (self.md5, self.sha256) = self.cloud._get_file_hashes(
            self.object_file.name)
        self.endpoint = self.cloud._object_store_client.get_endpoint()

    def test_create_object(self):

        self.register_uris([
            dict(method='GET',
                 uri='https://object-store.example.com/info',
                 json=dict(
                     swift={'max_file_size': 1000},
                     slo={'min_segment_size': 500})),
            dict(method='HEAD',
                 uri='{endpoint}/{container}/{object}'.format(
                     endpoint=self.endpoint, container=self.container,
                     object=self.object),
                 status_code=404),
            dict(method='PUT',
                 uri='{endpoint}/{container}/{object}'.format(
                     endpoint=self.endpoint,
                     container=self.container, object=self.object),
                 status_code=201,
                 validate=dict(
                     headers={
                         'x-object-meta-x-sdk-md5': self.md5,
                         'x-object-meta-x-sdk-sha256': self.sha256,
                     }))
        ])

        self.cloud.create_object(
            container=self.container, name=self.object,
            filename=self.object_file.name)

        self.assert_calls()

    def test_create_directory_marker_object(self):

        self.register_uris([
            dict(method='PUT',
                 uri='{endpoint}/{container}/{object}'.format(
                     endpoint=self.endpoint,
                     container=self.container, object=self.object),
                 status_code=201,
                 validate=dict(
                     headers={
                         'content-type': 'application/directory',
                     }))
        ])

        self.cloud.create_directory_marker_object(
            container=self.container, name=self.object)

        self.assert_calls()

    def test_create_dynamic_large_object(self):

        max_file_size = 2
        min_file_size = 1

        uris_to_mock = [
            dict(method='GET',
                 uri='https://object-store.example.com/info',
                 json=dict(
                     swift={'max_file_size': max_file_size},
                     slo={'min_segment_size': min_file_size})),
            dict(method='HEAD',
                 uri='{endpoint}/{container}/{object}'.format(
                     endpoint=self.endpoint, container=self.container,
                     object=self.object),
                 status_code=404)
        ]

        uris_to_mock.extend(
            [dict(method='PUT',
                  uri='{endpoint}/{container}/{object}/{index:0>6}'.format(
                      endpoint=self.endpoint,
                      container=self.container,
                      object=self.object,
                      index=index),
                  status_code=201)
                for index, offset in enumerate(
                    range(0, len(self.content), max_file_size))]
        )

        uris_to_mock.append(
            dict(method='PUT',
                 uri='{endpoint}/{container}/{object}'.format(
                     endpoint=self.endpoint,
                     container=self.container, object=self.object),
                 status_code=201,
                 validate=dict(
                     headers={
                         'x-object-manifest': '{container}/{object}'.format(
                             container=self.container, object=self.object),
                         'x-object-meta-x-sdk-md5': self.md5,
                         'x-object-meta-x-sdk-sha256': self.sha256,
                     })))
        self.register_uris(uris_to_mock)
        self.cloud.create_object(
            container=self.container, name=self.object,
            filename=self.object_file.name, use_slo=False)

        # After call 3, order become indeterminate because of thread pool
        self.assert_calls(stop_after=3)

        for key, value in self.calls[-1]['headers'].items():
            self.assertEqual(
                value, self.adapter.request_history[-1].headers[key],
                'header mismatch in manifest call')

    def test_create_static_large_object(self):

        max_file_size = 25
        min_file_size = 1

        uris_to_mock = [
            dict(method='GET', uri='https://object-store.example.com/info',
                 json=dict(
                     swift={'max_file_size': max_file_size},
                     slo={'min_segment_size': min_file_size})),
            dict(method='HEAD',
                 uri='{endpoint}/{container}/{object}'.format(
                     endpoint=self.endpoint,
                     container=self.container, object=self.object),
                 status_code=404)
        ]

        uris_to_mock.extend([
            dict(method='PUT',
                 uri='{endpoint}/{container}/{object}/{index:0>6}'.format(
                     endpoint=self.endpoint,
                     container=self.container,
                     object=self.object,
                     index=index),
                 status_code=201,
                 headers=dict(Etag='etag{index}'.format(index=index)))
            for index, offset in enumerate(
                range(0, len(self.content), max_file_size))
        ])

        uris_to_mock.append(
            dict(method='PUT',
                 uri='{endpoint}/{container}/{object}'.format(
                     endpoint=self.endpoint,
                     container=self.container, object=self.object),
                 status_code=201,
                 validate=dict(
                     params={
                         'multipart-manifest', 'put'
                     },
                     headers={
                         'x-object-meta-x-sdk-md5': self.md5,
                         'x-object-meta-x-sdk-sha256': self.sha256,
                     })))
        self.register_uris(uris_to_mock)

        self.cloud.create_object(
            container=self.container, name=self.object,
            filename=self.object_file.name, use_slo=True)

        # After call 3, order become indeterminate because of thread pool
        self.assert_calls(stop_after=3)

        for key, value in self.calls[-1]['headers'].items():
            self.assertEqual(
                value, self.adapter.request_history[-1].headers[key],
                'header mismatch in manifest call')

        base_object = '/{container}/{object}'.format(
            endpoint=self.endpoint,
            container=self.container,
            object=self.object)

        self.assertEqual([
            {
                'path': "{base_object}/000000".format(
                    base_object=base_object),
                'size_bytes': 25,
                'etag': 'etag0',
            },
            {
                'path': "{base_object}/000001".format(
                    base_object=base_object),
                'size_bytes': 25,
                'etag': 'etag1',
            },
            {
                'path': "{base_object}/000002".format(
                    base_object=base_object),
                'size_bytes': 25,
                'etag': 'etag2',
            },
            {
                'path': "{base_object}/000003".format(
                    base_object=base_object),
                'size_bytes': len(self.object) - 75,
                'etag': 'etag3',
            },
        ], self.adapter.request_history[-1].json())

    def test_slo_manifest_retry(self):
        """
        Uploading the SLO manifest file should be retried up to 3 times before
        giving up. This test should succeed on the 3rd and final attempt.
        """
        max_file_size = 25
        min_file_size = 1

        uris_to_mock = [
            dict(method='GET', uri='https://object-store.example.com/info',
                 json=dict(
                     swift={'max_file_size': max_file_size},
                     slo={'min_segment_size': min_file_size})),
            dict(method='HEAD',
                 uri='{endpoint}/{container}/{object}'.format(
                     endpoint=self.endpoint,
                     container=self.container, object=self.object),
                 status_code=404)
        ]

        uris_to_mock.extend([
            dict(method='PUT',
                 uri='{endpoint}/{container}/{object}/{index:0>6}'.format(
                     endpoint=self.endpoint,
                     container=self.container,
                     object=self.object,
                     index=index),
                 status_code=201,
                 headers=dict(Etag='etag{index}'.format(index=index)))
            for index, offset in enumerate(
                range(0, len(self.content), max_file_size))
        ])

        # manifest file upload calls
        uris_to_mock.extend([
            dict(method='PUT',
                 uri='{endpoint}/{container}/{object}'.format(
                     endpoint=self.endpoint,
                     container=self.container, object=self.object),
                 status_code=400,
                 validate=dict(
                     params={
                         'multipart-manifest', 'put'
                     },
                     headers={
                         'x-object-meta-x-sdk-md5': self.md5,
                         'x-object-meta-x-sdk-sha256': self.sha256,
                     })),
            dict(method='PUT',
                 uri='{endpoint}/{container}/{object}'.format(
                     endpoint=self.endpoint,
                     container=self.container, object=self.object),
                 status_code=400,
                 validate=dict(
                     params={
                         'multipart-manifest', 'put'
                     },
                     headers={
                         'x-object-meta-x-sdk-md5': self.md5,
                         'x-object-meta-x-sdk-sha256': self.sha256,
                     })),
            dict(method='PUT',
                 uri='{endpoint}/{container}/{object}'.format(
                     endpoint=self.endpoint,
                     container=self.container, object=self.object),
                 status_code=201,
                 validate=dict(
                     params={
                         'multipart-manifest', 'put'
                     },
                     headers={
                         'x-object-meta-x-sdk-md5': self.md5,
                         'x-object-meta-x-sdk-sha256': self.sha256,
                     })),
        ])

        self.register_uris(uris_to_mock)

        self.cloud.create_object(
            container=self.container, name=self.object,
            filename=self.object_file.name, use_slo=True)

        # After call 3, order become indeterminate because of thread pool
        self.assert_calls(stop_after=3)

        for key, value in self.calls[-1]['headers'].items():
            self.assertEqual(
                value, self.adapter.request_history[-1].headers[key],
                'header mismatch in manifest call')

        base_object = '/{container}/{object}'.format(
            endpoint=self.endpoint,
            container=self.container,
            object=self.object)

        self.assertEqual([
            {
                'path': "{base_object}/000000".format(
                    base_object=base_object),
                'size_bytes': 25,
                'etag': 'etag0',
            },
            {
                'path': "{base_object}/000001".format(
                    base_object=base_object),
                'size_bytes': 25,
                'etag': 'etag1',
            },
            {
                'path': "{base_object}/000002".format(
                    base_object=base_object),
                'size_bytes': 25,
                'etag': 'etag2',
            },
            {
                'path': "{base_object}/000003".format(
                    base_object=base_object),
                'size_bytes': len(self.object) - 75,
                'etag': 'etag3',
            },
        ], self.adapter.request_history[-1].json())

    def test_slo_manifest_fail(self):
        """
        Uploading the SLO manifest file should be retried up to 3 times before
        giving up. This test fails all 3 attempts and should verify that we
        delete uploaded segments that begin with the object prefix.
        """
        max_file_size = 25
        min_file_size = 1

        uris_to_mock = [
            dict(method='GET', uri='https://object-store.example.com/info',
                 json=dict(
                     swift={'max_file_size': max_file_size},
                     slo={'min_segment_size': min_file_size})),
            dict(method='HEAD',
                 uri='{endpoint}/{container}/{object}'.format(
                     endpoint=self.endpoint,
                     container=self.container, object=self.object),
                 status_code=404)
        ]

        uris_to_mock.extend([
            dict(method='PUT',
                 uri='{endpoint}/{container}/{object}/{index:0>6}'.format(
                     endpoint=self.endpoint,
                     container=self.container,
                     object=self.object,
                     index=index),
                 status_code=201,
                 headers=dict(Etag='etag{index}'.format(index=index)))
            for index, offset in enumerate(
                range(0, len(self.content), max_file_size))
        ])

        # manifest file upload calls
        uris_to_mock.extend([
            dict(method='PUT',
                 uri='{endpoint}/{container}/{object}'.format(
                     endpoint=self.endpoint,
                     container=self.container, object=self.object),
                 status_code=400,
                 validate=dict(
                     params={
                         'multipart-manifest', 'put'
                     },
                     headers={
                         'x-object-meta-x-sdk-md5': self.md5,
                         'x-object-meta-x-sdk-sha256': self.sha256,
                     })),
            dict(method='PUT',
                 uri='{endpoint}/{container}/{object}'.format(
                     endpoint=self.endpoint,
                     container=self.container, object=self.object),
                 status_code=400,
                 validate=dict(
                     params={
                         'multipart-manifest', 'put'
                     },
                     headers={
                         'x-object-meta-x-sdk-md5': self.md5,
                         'x-object-meta-x-sdk-sha256': self.sha256,
                     })),
            dict(method='PUT',
                 uri='{endpoint}/{container}/{object}'.format(
                     endpoint=self.endpoint,
                     container=self.container, object=self.object),
                 status_code=400,
                 validate=dict(
                     params={
                         'multipart-manifest', 'put'
                     },
                     headers={
                         'x-object-meta-x-sdk-md5': self.md5,
                         'x-object-meta-x-sdk-sha256': self.sha256,
                     })),
        ])

        # Cleaning up image upload segments involves calling the
        # delete_autocreated_image_objects() API method which will list
        # objects (LIST), get the object metadata (HEAD), then delete the
        # object (DELETE).
        uris_to_mock.extend([
            dict(method='GET',
                 uri='{endpoint}/images?format=json&prefix={prefix}'.format(
                     endpoint=self.endpoint,
                     prefix=self.object),
                 complete_qs=True,
                 json=[{
                     'content_type': 'application/octet-stream',
                     'bytes': 1437258240,
                     'hash': '249219347276c331b87bf1ac2152d9af',
                     'last_modified': '2015-02-16T17:50:05.289600',
                     'name': self.object
                 }]),

            dict(method='HEAD',
                 uri='{endpoint}/images/{object}'.format(
                     endpoint=self.endpoint,
                     object=self.object),
                 headers={
                     'X-Timestamp': '1429036140.50253',
                     'X-Trans-Id': 'txbbb825960a3243b49a36f-005a0dadaedfw1',
                     'Content-Length': '1290170880',
                     'Last-Modified': 'Tue, 14 Apr 2015 18:29:01 GMT',
                     'x-object-meta-x-sdk-autocreated': 'true',
                     'X-Object-Meta-X-Shade-Sha256': 'does not matter',
                     'X-Object-Meta-X-Shade-Md5': 'does not matter',
                     'Date': 'Thu, 16 Nov 2017 15:24:30 GMT',
                     'Accept-Ranges': 'bytes',
                     'Content-Type': 'application/octet-stream',
                     'Etag': '249219347276c331b87bf1ac2152d9af',
                 }),

            dict(method='DELETE',
                 uri='{endpoint}/images/{object}'.format(
                     endpoint=self.endpoint, object=self.object))
        ])

        self.register_uris(uris_to_mock)

        # image_api_use_tasks needs to be set to True in order for the API
        # method delete_autocreated_image_objects() to do the cleanup.
        self.cloud.image_api_use_tasks = True

        self.assertRaises(
            exc.OpenStackCloudException,
            self.cloud.create_object,
            container=self.container, name=self.object,
            filename=self.object_file.name, use_slo=True)

        # After call 3, order become indeterminate because of thread pool
        self.assert_calls(stop_after=3)

    def test_object_segment_retry_failure(self):

        max_file_size = 25
        min_file_size = 1

        self.register_uris([
            dict(method='GET', uri='https://object-store.example.com/info',
                 json=dict(
                     swift={'max_file_size': max_file_size},
                     slo={'min_segment_size': min_file_size})),
            dict(method='HEAD',
                 uri='{endpoint}/{container}/{object}'.format(
                     endpoint=self.endpoint,
                     container=self.container, object=self.object),
                 status_code=404),
            dict(method='PUT',
                 uri='{endpoint}/{container}/{object}/000000'.format(
                     endpoint=self.endpoint,
                     container=self.container,
                     object=self.object),
                 status_code=201),
            dict(method='PUT',
                 uri='{endpoint}/{container}/{object}/000001'.format(
                     endpoint=self.endpoint,
                     container=self.container,
                     object=self.object),
                 status_code=201),
            dict(method='PUT',
                 uri='{endpoint}/{container}/{object}/000002'.format(
                     endpoint=self.endpoint,
                     container=self.container,
                     object=self.object),
                 status_code=201),
            dict(method='PUT',
                 uri='{endpoint}/{container}/{object}/000003'.format(
                     endpoint=self.endpoint,
                     container=self.container,
                     object=self.object),
                 status_code=501),
            dict(method='PUT',
                 uri='{endpoint}/{container}/{object}'.format(
                     endpoint=self.endpoint,
                     container=self.container, object=self.object),
                 status_code=201)
        ])

        self.assertRaises(
            exc.OpenStackCloudException,
            self.cloud.create_object,
            container=self.container, name=self.object,
            filename=self.object_file.name, use_slo=True)

        # After call 3, order become indeterminate because of thread pool
        self.assert_calls(stop_after=3)

    def test_object_segment_retries(self):

        max_file_size = 25
        min_file_size = 1

        self.register_uris([
            dict(method='GET', uri='https://object-store.example.com/info',
                 json=dict(
                     swift={'max_file_size': max_file_size},
                     slo={'min_segment_size': min_file_size})),
            dict(method='HEAD',
                 uri='{endpoint}/{container}/{object}'.format(
                     endpoint=self.endpoint,
                     container=self.container, object=self.object),
                 status_code=404),
            dict(method='PUT',
                 uri='{endpoint}/{container}/{object}/000000'.format(
                     endpoint=self.endpoint,
                     container=self.container,
                     object=self.object),
                 headers={'etag': 'etag0'},
                 status_code=201),
            dict(method='PUT',
                 uri='{endpoint}/{container}/{object}/000001'.format(
                     endpoint=self.endpoint,
                     container=self.container,
                     object=self.object),
                 headers={'etag': 'etag1'},
                 status_code=201),
            dict(method='PUT',
                 uri='{endpoint}/{container}/{object}/000002'.format(
                     endpoint=self.endpoint,
                     container=self.container,
                     object=self.object),
                 headers={'etag': 'etag2'},
                 status_code=201),
            dict(method='PUT',
                 uri='{endpoint}/{container}/{object}/000003'.format(
                     endpoint=self.endpoint,
                     container=self.container,
                     object=self.object),
                 status_code=501),
            dict(method='PUT',
                 uri='{endpoint}/{container}/{object}/000003'.format(
                     endpoint=self.endpoint,
                     container=self.container,
                     object=self.object),
                 status_code=201,
                 headers={'etag': 'etag3'}),
            dict(method='PUT',
                 uri='{endpoint}/{container}/{object}'.format(
                     endpoint=self.endpoint,
                     container=self.container, object=self.object),
                 status_code=201,
                 validate=dict(
                     params={
                         'multipart-manifest', 'put'
                     },
                     headers={
                         'x-object-meta-x-sdk-md5': self.md5,
                         'x-object-meta-x-sdk-sha256': self.sha256,
                     }))
        ])

        self.cloud.create_object(
            container=self.container, name=self.object,
            filename=self.object_file.name, use_slo=True)

        # After call 3, order become indeterminate because of thread pool
        self.assert_calls(stop_after=3)

        for key, value in self.calls[-1]['headers'].items():
            self.assertEqual(
                value, self.adapter.request_history[-1].headers[key],
                'header mismatch in manifest call')

        base_object = '/{container}/{object}'.format(
            endpoint=self.endpoint,
            container=self.container,
            object=self.object)

        self.assertEqual([
            {
                'path': "{base_object}/000000".format(
                    base_object=base_object),
                'size_bytes': 25,
                'etag': 'etag0',
            },
            {
                'path': "{base_object}/000001".format(
                    base_object=base_object),
                'size_bytes': 25,
                'etag': 'etag1',
            },
            {
                'path': "{base_object}/000002".format(
                    base_object=base_object),
                'size_bytes': 25,
                'etag': 'etag2',
            },
            {
                'path': "{base_object}/000003".format(
                    base_object=base_object),
                'size_bytes': len(self.object) - 75,
                'etag': 'etag3',
            },
        ], self.adapter.request_history[-1].json())

    def test_create_object_skip_checksum(self):

        self.register_uris([
            dict(method='GET',
                 uri='https://object-store.example.com/info',
                 json=dict(
                     swift={'max_file_size': 1000},
                     slo={'min_segment_size': 500})),
            dict(method='HEAD',
                 uri='{endpoint}/{container}/{object}'.format(
                     endpoint=self.endpoint, container=self.container,
                     object=self.object),
                 status_code=200),
            dict(method='PUT',
                 uri='{endpoint}/{container}/{object}'.format(
                     endpoint=self.endpoint,
                     container=self.container, object=self.object),
                 status_code=201,
                 validate=dict(headers={})),
        ])

        self.cloud.create_object(
            container=self.container, name=self.object,
            filename=self.object_file.name,
            generate_checksums=False)

        self.assert_calls()

    def test_create_object_data(self):

        self.register_uris([
            dict(method='PUT',
                 uri='{endpoint}/{container}/{object}'.format(
                     endpoint=self.endpoint,
                     container=self.container, object=self.object),
                 status_code=201,
                 validate=dict(
                     headers={},
                     data=self.content,
                 )),
        ])

        self.cloud.create_object(
            container=self.container, name=self.object,
            data=self.content)

        self.assert_calls()
