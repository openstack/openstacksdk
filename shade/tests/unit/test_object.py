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

import testtools

import shade
import shade.openstackcloud
from shade import exc
from shade.tests.unit import base


class TestObject(base.RequestsMockTestCase):

    def setUp(self):
        super(TestObject, self).setUp()

        self.container = self.getUniqueString()
        self.object = self.getUniqueString()
        self.endpoint = self.cloud._object_store_client.get_endpoint()
        self.container_endpoint = '{endpoint}/{container}'.format(
            endpoint=self.endpoint, container=self.container)
        self.object_endpoint = '{endpoint}/{object}'.format(
            endpoint=self.container_endpoint, object=self.object)

    def test_create_container(self):
        """Test creating a (private) container"""
        self.adapter.head(
            self.container_endpoint,
            [
                dict(status_code=404),
                dict(headers={
                    'Content-Length': '0',
                    'X-Container-Object-Count': '0',
                    'Accept-Ranges': 'bytes',
                    'X-Storage-Policy': 'Policy-0',
                    'Date': 'Fri, 16 Dec 2016 18:29:05 GMT',
                    'X-Timestamp': '1481912480.41664',
                    'X-Trans-Id': 'tx60ec128d9dbf44b9add68-0058543271dfw1',
                    'X-Container-Bytes-Used': '0',
                    'Content-Type': 'text/plain; charset=utf-8'}),
            ])
        self.adapter.put(
            self.container_endpoint,
            status_code=201,
            headers={
                'Date': 'Fri, 16 Dec 2016 18:21:20 GMT',
                'Content-Length': '0',
                'Content-Type': 'text/html; charset=UTF-8',
            })

        self.cloud.create_container(self.container)

        self.calls += [
            dict(method='HEAD', url=self.container_endpoint),
            dict(method='PUT', url=self.container_endpoint),
            dict(method='HEAD', url=self.container_endpoint),
        ]
        self.assert_calls()

    def test_create_container_public(self):
        """Test creating a public container"""
        self.adapter.head(
            self.container_endpoint,
            [
                dict(status_code=404),
                dict(headers={
                    'Content-Length': '0',
                    'X-Container-Object-Count': '0',
                    'Accept-Ranges': 'bytes',
                    'X-Storage-Policy': 'Policy-0',
                    'Date': 'Fri, 16 Dec 2016 18:29:05 GMT',
                    'X-Timestamp': '1481912480.41664',
                    'X-Trans-Id': 'tx60ec128d9dbf44b9add68-0058543271dfw1',
                    'X-Container-Bytes-Used': '0',
                    'Content-Type': 'text/plain; charset=utf-8'}),
            ])
        self.adapter.put(
            self.container_endpoint,
            status_code=201,
            headers={
                'Date': 'Fri, 16 Dec 2016 18:21:20 GMT',
                'Content-Length': '0',
                'Content-Type': 'text/html; charset=UTF-8',
            })
        self.adapter.post(
            self.container_endpoint,
            status_code=201)

        self.cloud.create_container(self.container, public=True)

        self.calls += [
            dict(method='HEAD', url=self.container_endpoint),
            dict(
                method='PUT',
                url=self.container_endpoint),
            dict(
                method='POST',
                url=self.container_endpoint,
                headers={
                    'x-container-read':
                    shade.openstackcloud.OBJECT_CONTAINER_ACLS['public']}),
            dict(method='HEAD', url=self.container_endpoint),
        ]
        self.assert_calls()

    def test_create_container_exists(self):
        """Test creating a container that exists."""
        self.adapter.head(
            self.container_endpoint,
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

        container = self.cloud.create_container(self.container)

        self.calls += [
            dict(method='HEAD', url=self.container_endpoint),
        ]
        self.assert_calls()
        self.assertIsNotNone(container)

    def test_delete_container(self):
        self.adapter.delete(self.container_endpoint)
        deleted = self.cloud.delete_container(self.container)
        self.calls += [
            dict(method='DELETE', url=self.container_endpoint),
        ]
        self.assert_calls()
        # TODO(mordred) This should be True/False not None all the time
        self.assertIsNone(deleted)

    def test_delete_container_404(self):
        """No exception when deleting a container that does not exist"""
        self.adapter.delete(
            self.container_endpoint,
            status_code=404)
        deleted = self.cloud.delete_container(self.container)
        self.calls += [
            dict(method='DELETE', url=self.container_endpoint),
        ]
        self.assert_calls()
        # TODO(mordred) This should be True/False not None all the time
        self.assertIsNone(deleted)

    def test_delete_container_error(self):
        """Non-404 swift error re-raised as OSCE"""
        self.adapter.delete(
            self.container_endpoint,
            status_code=409)
        self.assertRaises(
            shade.OpenStackCloudException,
            self.cloud.delete_container, self.container)
        self.calls += [
            dict(method='DELETE', url=self.container_endpoint),
        ]
        self.assert_calls()

    def test_update_container(self):
        self.adapter.post(
            self.container_endpoint,
            status_code=204)
        headers = {'x-container-read':
                   shade.openstackcloud.OBJECT_CONTAINER_ACLS['public']}
        assert_headers = headers.copy()

        self.cloud.update_container(self.container, headers)

        self.calls += [
            dict(
                method='POST',
                url=self.container_endpoint,
                headers=assert_headers),
        ]
        self.assert_calls()

    def test_update_container_error(self):
        """Swift error re-raised as OSCE"""
        # This test is of questionable value - the swift API docs do not
        # declare error codes (other than 404 for the container) for this
        # method, and I cannot make a synthetic failure to validate a real
        # error code. So we're really just testing the shade adapter error
        # raising logic here, rather than anything specific to swift.
        self.adapter.post(
            self.container_endpoint,
            status_code=409)
        self.assertRaises(
            shade.OpenStackCloudException,
            self.cloud.update_container, self.container, dict(foo='bar'))

    def test_set_container_access_public(self):
        self.adapter.post(
            self.container_endpoint,
            status_code=204)

        self.cloud.set_container_access(self.container, 'public')

        self.calls += [
            dict(
                method='POST',
                url=self.container_endpoint,
                headers={
                    'x-container-read':
                    shade.openstackcloud.OBJECT_CONTAINER_ACLS['public']}),
        ]
        self.assert_calls()

    def test_set_container_access_private(self):
        self.adapter.post(
            self.container_endpoint,
            status_code=204)

        self.cloud.set_container_access(self.container, 'private')

        self.calls += [
            dict(
                method='POST',
                url=self.container_endpoint,
                headers={
                    'x-container-read':
                    shade.openstackcloud.OBJECT_CONTAINER_ACLS['private']}),
        ]
        self.assert_calls()

    def test_set_container_access_invalid(self):
        self.assertRaises(
            shade.OpenStackCloudException,
            self.cloud.set_container_access, self.container, 'invalid')

    def test_get_container_access(self):
        self.adapter.head(
            self.container_endpoint,
            headers={
                'x-container-read':
                str(shade.openstackcloud.OBJECT_CONTAINER_ACLS['public'])})

        access = self.cloud.get_container_access(self.container)
        self.assertEqual('public', access)

    def test_get_container_invalid(self):
        self.adapter.head(
            self.container_endpoint,
            headers={
                'x-container-read': 'invalid'})

        with testtools.ExpectedException(
                exc.OpenStackCloudException,
                "Could not determine container access for ACL: invalid"
        ):
            self.cloud.get_container_access(self.container)

    def test_get_container_access_not_found(self):
        self.adapter.head(
            self.container_endpoint,
            status_code=404)
        with testtools.ExpectedException(
                exc.OpenStackCloudException,
                "Container not found: %s" % self.container
        ):
            self.cloud.get_container_access(self.container)

    def test_list_containers(self):
        # TODO(mordred) swiftclient sends format=json in the query string
        # we'll want to send it in the accept header. Also, swiftclient
        # always sends a second GET with marker set to the name of the last
        # element returned previously. We should be able to infer if this is
        # needed by checking swfit.account_listing_limit in the capabilities
        # OR by looking at the value of 'X-Account-Container-Count' in the
        # returned headers and seeing if it's larger than the number of
        # containers returned.
        first = '{endpoint}?format=json'.format(
            endpoint=self.endpoint)
        second = '{endpoint}?format=json&marker={first}'.format(
            endpoint=self.endpoint, first=self.container)
        containers = [
            {u'count': 0, u'bytes': 0, u'name': self.container}]

        self.adapter.get(first, complete_qs=True, json=containers)
        self.adapter.get(second, complete_qs=True, status_code=204)

        ret = self.cloud.list_containers()
        self.calls += [
            dict(method='GET', url=first),
            dict(method='GET', url=second),
        ]
        self.assert_calls()
        self.assertEqual(containers, ret)

    def test_list_containers_not_full(self):
        endpoint = '{endpoint}?format=json'.format(
            endpoint=self.endpoint)
        containers = [
            {u'count': 0, u'bytes': 0, u'name': self.container}]

        self.adapter.get(endpoint, complete_qs=True, json=containers)

        ret = self.cloud.list_containers(full_listing=False)

        self.calls += [
            dict(method='GET', url=endpoint),
        ]
        self.assert_calls()
        self.assertEqual(containers, ret)

    def test_list_containers_exception(self):
        # TODO(mordred) There are no error codes I can see. The 409 is fake.
        endpoint = '{endpoint}?format=json'.format(
            endpoint=self.endpoint)
        self.adapter.get(endpoint, complete_qs=True, status_code=409)

        self.assertRaises(
            exc.OpenStackCloudException, self.cloud.list_containers)

    def test_list_objects(self):
        first = '{endpoint}?format=json'.format(
            endpoint=self.container_endpoint)
        second = '{endpoint}?format=json&marker={first}'.format(
            endpoint=self.container_endpoint, first=self.object)

        objects = [{
            u'bytes': 20304400896,
            u'last_modified': u'2016-12-15T13:34:13.650090',
            u'hash': u'daaf9ed2106d09bba96cf193d866445e',
            u'name': self.object,
            u'content_type': u'application/octet-stream'}]

        self.adapter.get(first, complete_qs=True, json=objects)
        self.adapter.get(second, complete_qs=True, status_code=204)

        ret = self.cloud.list_objects(self.container)

        self.calls += [
            dict(method='GET', url=first),
            dict(method='GET', url=second),
        ]
        self.assert_calls()
        self.assertEqual(objects, ret)

    def test_list_objects_not_full(self):
        endpoint = '{endpoint}?format=json'.format(
            endpoint=self.container_endpoint)

        objects = [{
            u'bytes': 20304400896,
            u'last_modified': u'2016-12-15T13:34:13.650090',
            u'hash': u'daaf9ed2106d09bba96cf193d866445e',
            u'name': self.object,
            u'content_type': u'application/octet-stream'}]

        self.adapter.get(endpoint, complete_qs=True, json=objects)

        ret = self.cloud.list_objects(self.container, full_listing=False)

        self.calls += [
            dict(method='GET', url=endpoint),
        ]
        self.assert_calls()
        self.assertEqual(objects, ret)

    def test_list_objects_exception(self):
        endpoint = '{endpoint}?format=json'.format(
            endpoint=self.container_endpoint)
        self.adapter.get(endpoint, complete_qs=True, status_code=409)
        self.assertRaises(
            exc.OpenStackCloudException,
            self.cloud.list_objects, self.container)

    def test_delete_object(self):
        # TODO(mordred) calling get_object_metadata first is stupid. We should
        # just make the delete call and if it 404's, then the object didn't
        # exist.
        self.adapter.head(
            self.object_endpoint,
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
            })
        self.adapter.delete(self.object_endpoint, status_code=204)

        self.assertTrue(self.cloud.delete_object(self.container, self.object))

        self.calls += [
            dict(method='HEAD', url=self.object_endpoint),
            dict(method='DELETE', url=self.object_endpoint),
        ]
        self.assert_calls()

    def test_delete_object_not_found(self):
        self.adapter.head(self.object_endpoint, status_code=404)

        self.assertFalse(self.cloud.delete_object(self.container, self.object))

        self.calls += [
            dict(method='HEAD', url=self.object_endpoint),
        ]
        self.assert_calls()

    def test_delete_object_exception(self):
        self.adapter.head(
            self.object_endpoint,
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
            })

        # TODO(mordred) This version of the code is prone to race conditions
        # When we stop doing HEAD first, we can kill this test.
        self.adapter.delete(self.object_endpoint, status_code=404)

        self.assertRaises(
            shade.OpenStackCloudException,
            self.cloud.delete_object,
            self.container,
            self.object)

        self.calls += [
            dict(method='HEAD', url=self.object_endpoint),
            dict(method='DELETE', url=self.object_endpoint),
        ]
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
        # TODO(mordred) Is this a bug in requests_mock or swiftclient that
        # I have to mark this as b'test body' ?
        text = b'test body'
        self.adapter.get(
            self.object_endpoint,
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
            text='test body')

        resp = self.cloud.get_object(self.container, self.object)

        self.calls += [
            dict(method='GET', url=self.object_endpoint),
        ]
        self.assert_calls()

        self.assertEqual((response_headers, text), resp)

    def test_get_object_not_found(self):
        self.adapter.get(self.object_endpoint, status_code=404)

        self.assertIsNone(self.cloud.get_object(self.container, self.object))

        self.calls += [
            dict(method='GET', url=self.object_endpoint),
        ]
        self.assert_calls()

    def test_get_object_exception(self):
        # TODO(mordred) Bogus error code - what are we testing here?
        self.adapter.get(self.object_endpoint, status_code=409)

        self.assertRaises(
            shade.OpenStackCloudException,
            self.cloud.get_object,
            self.container, self.object)

        self.calls += [
            dict(method='GET', url=self.object_endpoint),
        ]
        self.assert_calls()

    def test_get_object_segment_size(self):
        self.adapter.get(
            'https://object-store.example.com/info',
            json=dict(
                swift={'max_file_size': 1000},
                slo={'min_segment_size': 500}))
        self.assertEqual(500, self.cloud.get_object_segment_size(400))
        self.assertEqual(900, self.cloud.get_object_segment_size(900))
        self.assertEqual(1000, self.cloud.get_object_segment_size(1000))
        self.assertEqual(1000, self.cloud.get_object_segment_size(1100))

    def test_get_object_segment_size_http_404(self):
        self.adapter.get(
            'https://object-store.example.com/info',
            status_code=404,
            reason='Not Found')
        self.assertEqual(shade.openstackcloud.DEFAULT_OBJECT_SEGMENT_SIZE,
                         self.cloud.get_object_segment_size(None))

    def test_get_object_segment_size_http_412(self):
        self.adapter.get(
            'https://object-store.example.com/info',
            status_code=412,
            reason='Precondition failed')
        self.assertEqual(shade.openstackcloud.DEFAULT_OBJECT_SEGMENT_SIZE,
                         self.cloud.get_object_segment_size(None))
