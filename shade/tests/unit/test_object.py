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

import testtools

import shade
import shade.openstackcloud
from shade import exc
from shade.tests.unit import base


class BaseTestObject(base.RequestsMockTestCase):

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
                             shade.openstackcloud.OBJECT_CONTAINER_ACLS[
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
            shade.OpenStackCloudException,
            self.cloud.delete_container, self.container)
        self.assert_calls()

    def test_update_container(self):
        headers = {
            'x-container-read':
            shade.openstackcloud.OBJECT_CONTAINER_ACLS['public']}
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
            shade.OpenStackCloudException,
            self.cloud.update_container, self.container, dict(foo='bar'))
        self.assert_calls()

    def test_set_container_access_public(self):
        self.register_uris([
            dict(method='POST', uri=self.container_endpoint,
                 status_code=204,
                 validate=dict(
                     headers={
                         'x-container-read':
                             shade.openstackcloud.OBJECT_CONTAINER_ACLS[
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
                             shade.openstackcloud.OBJECT_CONTAINER_ACLS[
                                 'private']}))])

        self.cloud.set_container_access(self.container, 'private')

        self.assert_calls()

    def test_set_container_access_invalid(self):
        self.assertRaises(
            shade.OpenStackCloudException,
            self.cloud.set_container_access, self.container, 'invalid')

    def test_get_container_access(self):
        self.register_uris([
            dict(method='HEAD', uri=self.container_endpoint,
                 headers={
                     'x-container-read':
                         str(shade.openstackcloud.OBJECT_CONTAINER_ACLS[
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

    def test_get_object_not_found(self):
        self.register_uris([dict(method='GET',
                                 uri=self.object_endpoint, status_code=404)])

        self.assertIsNone(self.cloud.get_object(self.container, self.object))

        self.assert_calls()

    def test_get_object_exception(self):
        self.register_uris([dict(method='GET', uri=self.object_endpoint,
                                 status_code=416)])

        self.assertRaises(
            shade.OpenStackCloudException,
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
        self.assertEqual(shade.openstackcloud.DEFAULT_OBJECT_SEGMENT_SIZE,
                         self.cloud.get_object_segment_size(None))
        self.assert_calls()

    def test_get_object_segment_size_http_412(self):
        self.register_uris([
            dict(method='GET', uri='https://object-store.example.com/info',
                 status_code=412, reason='Precondition failed')])
        self.assertEqual(shade.openstackcloud.DEFAULT_OBJECT_SEGMENT_SIZE,
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
                 uri='{endpoint}/{container}'.format(
                     endpoint=self.endpoint,
                     container=self.container),
                 status_code=404),
            dict(method='PUT',
                 uri='{endpoint}/{container}'.format(
                     endpoint=self.endpoint, container=self.container),
                 status_code=201,
                 headers={
                     'Date': 'Fri, 16 Dec 2016 18:21:20 GMT',
                     'Content-Length': '0',
                     'Content-Type': 'text/html; charset=UTF-8',
                 }),
            dict(method='HEAD',
                 uri='{endpoint}/{container}'.format(
                     endpoint=self.endpoint, container=self.container),
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
                         'x-object-meta-x-shade-md5': self.md5,
                         'x-object-meta-x-shade-sha256': self.sha256,
                     }))
        ])

        self.cloud.create_object(
            container=self.container, name=self.object,
            filename=self.object_file.name)

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
                 uri='{endpoint}/{container}'.format(
                     endpoint=self.endpoint,
                     container=self.container),
                 status_code=404),
            dict(method='PUT',
                 uri='{endpoint}/{container}'.format(
                     endpoint=self.endpoint,
                     container=self.container, ),
                 status_code=201,
                 headers={
                     'Date': 'Fri, 16 Dec 2016 18:21:20 GMT',
                     'Content-Length': '0',
                     'Content-Type': 'text/html; charset=UTF-8',
                 }),
            dict(method='HEAD',
                 uri='{endpoint}/{container}'.format(
                     endpoint=self.endpoint,
                     container=self.container),
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
                         'x-object-meta-x-shade-md5': self.md5,
                         'x-object-meta-x-shade-sha256': self.sha256,
                     })))
        self.register_uris(uris_to_mock)
        self.cloud.create_object(
            container=self.container, name=self.object,
            filename=self.object_file.name, use_slo=False)

        # After call 6, order become indeterminate because of thread pool
        self.assert_calls(stop_after=6)

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
                 uri='{endpoint}/{container}'.format(
                     endpoint=self.endpoint,
                     container=self.container),
                 status_code=404),
            dict(method='PUT',
                 uri='{endpoint}/{container}'.format(
                     endpoint=self.endpoint,
                     container=self.container, ),
                 status_code=201,
                 headers={
                     'Date': 'Fri, 16 Dec 2016 18:21:20 GMT',
                     'Content-Length': '0',
                     'Content-Type': 'text/html; charset=UTF-8',
                 }),
            dict(method='HEAD',
                 uri='{endpoint}/{container}'.format(
                     endpoint=self.endpoint,
                     container=self.container),
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
                         'x-object-meta-x-shade-md5': self.md5,
                         'x-object-meta-x-shade-sha256': self.sha256,
                     })))
        self.register_uris(uris_to_mock)

        self.cloud.create_object(
            container=self.container, name=self.object,
            filename=self.object_file.name, use_slo=True)

        # After call 6, order become indeterminate because of thread pool
        self.assert_calls(stop_after=6)

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
                'size_bytes': 5,
                'etag': 'etag3',
            },
        ], self.adapter.request_history[-1].json())

    def test_object_segment_retry_failure(self):

        max_file_size = 25
        min_file_size = 1

        self.register_uris([
            dict(method='GET', uri='https://object-store.example.com/info',
                 json=dict(
                     swift={'max_file_size': max_file_size},
                     slo={'min_segment_size': min_file_size})),
            dict(method='HEAD',
                 uri='{endpoint}/{container}'.format(
                     endpoint=self.endpoint,
                     container=self.container),
                 status_code=404),
            dict(method='PUT',
                 uri='{endpoint}/{container}'.format(
                     endpoint=self.endpoint,
                     container=self.container, ),
                 status_code=201,
                 headers={
                     'Date': 'Fri, 16 Dec 2016 18:21:20 GMT',
                     'Content-Length': '0',
                     'Content-Type': 'text/html; charset=UTF-8',
                 }),
            dict(method='HEAD',
                 uri='{endpoint}/{container}'.format(
                     endpoint=self.endpoint,
                     container=self.container),
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

        # After call 6, order become indeterminate because of thread pool
        self.assert_calls(stop_after=6)

    def test_object_segment_retries(self):

        max_file_size = 25
        min_file_size = 1

        self.register_uris([
            dict(method='GET', uri='https://object-store.example.com/info',
                 json=dict(
                     swift={'max_file_size': max_file_size},
                     slo={'min_segment_size': min_file_size})),
            dict(method='HEAD',
                 uri='{endpoint}/{container}'.format(
                     endpoint=self.endpoint,
                     container=self.container),
                 status_code=404),
            dict(method='PUT',
                 uri='{endpoint}/{container}'.format(
                     endpoint=self.endpoint,
                     container=self.container, ),
                 status_code=201,
                 headers={
                     'Date': 'Fri, 16 Dec 2016 18:21:20 GMT',
                     'Content-Length': '0',
                     'Content-Type': 'text/html; charset=UTF-8',
                 }),
            dict(method='HEAD',
                 uri='{endpoint}/{container}'.format(
                     endpoint=self.endpoint,
                     container=self.container),
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
                         'x-object-meta-x-shade-md5': self.md5,
                         'x-object-meta-x-shade-sha256': self.sha256,
                     }))
        ])

        self.cloud.create_object(
            container=self.container, name=self.object,
            filename=self.object_file.name, use_slo=True)

        # After call 6, order become indeterminate because of thread pool
        self.assert_calls(stop_after=6)

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
                'size_bytes': 1,
                'etag': 'etag3',
            },
        ], self.adapter.request_history[-1].json())
