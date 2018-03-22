# Copyright 2016 Hewlett-Packard Development Company, L.P.
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

# TODO(mordred) There are mocks of the image_client in here that are not
#               using requests_mock. Erradicate them.

import operator
import tempfile
import uuid

import mock
import munch
import six

import openstack.cloud
from openstack.cloud import exc
from openstack.cloud import meta
from openstack.cloud import openstackcloud
from openstack.tests import fakes
from openstack.tests.unit import base


CINDER_URL = 'https://volume.example.com/v2/1c36b64c840a42cd9e9b931a369337f0'


class BaseTestImage(base.TestCase):

    def setUp(self):
        super(BaseTestImage, self).setUp()
        self.image_id = str(uuid.uuid4())
        self.image_name = self.getUniqueString('image')
        self.object_name = u'images/{name}'.format(name=self.image_name)
        self.imagefile = tempfile.NamedTemporaryFile(delete=False)
        self.imagefile.write(b'\0')
        self.imagefile.close()
        self.fake_image_dict = fakes.make_fake_image(
            image_id=self.image_id, image_name=self.image_name)
        self.fake_search_return = {'images': [self.fake_image_dict]}
        self.output = uuid.uuid4().bytes
        self.container_name = self.getUniqueString('container')


class TestImage(BaseTestImage):

    def setUp(self):
        super(TestImage, self).setUp()
        self.use_glance()

    def test_config_v1(self):
        self.cloud.config.config['image_api_version'] = '1'
        # We override the scheme of the endpoint with the scheme of the service
        # because glance has a bug where it doesn't return https properly.
        self.assertEqual(
            'https://image.example.com/v1/',
            self.cloud._image_client.get_endpoint())
        self.assertEqual(
            '1', self.cloud_config.get_api_version('image'))

    def test_config_v2(self):
        self.cloud.config.config['image_api_version'] = '2'
        # We override the scheme of the endpoint with the scheme of the service
        # because glance has a bug where it doesn't return https properly.
        self.assertEqual(
            'https://image.example.com/v2/',
            self.cloud._image_client.get_endpoint())
        self.assertEqual(
            '2', self.cloud_config.get_api_version('image'))

    def test_download_image_no_output(self):
        self.assertRaises(exc.OpenStackCloudException,
                          self.cloud.download_image, self.image_name)

    def test_download_image_two_outputs(self):
        fake_fd = six.BytesIO()
        self.assertRaises(exc.OpenStackCloudException,
                          self.cloud.download_image, self.image_name,
                          output_path='fake_path', output_file=fake_fd)

    def test_download_image_no_images_found(self):
        self.register_uris([
            dict(method='GET',
                 uri='https://image.example.com/v2/images',
                 json=dict(images=[]))])
        self.assertRaises(exc.OpenStackCloudResourceNotFound,
                          self.cloud.download_image, self.image_name,
                          output_path='fake_path')
        self.assert_calls()

    def _register_image_mocks(self):
        self.register_uris([
            dict(method='GET',
                 uri='https://image.example.com/v2/images',
                 json=self.fake_search_return),
            dict(method='GET',
                 uri='https://image.example.com/v2/images/{id}/file'.format(
                     id=self.image_id),
                 content=self.output,
                 headers={'Content-Type': 'application/octet-stream'})
        ])

    def test_download_image_with_fd(self):
        self._register_image_mocks()
        output_file = six.BytesIO()
        self.cloud.download_image(self.image_name, output_file=output_file)
        output_file.seek(0)
        self.assertEqual(output_file.read(), self.output)
        self.assert_calls()

    def test_download_image_with_path(self):
        self._register_image_mocks()
        output_file = tempfile.NamedTemporaryFile()
        self.cloud.download_image(
            self.image_name, output_path=output_file.name)
        output_file.seek(0)
        self.assertEqual(output_file.read(), self.output)
        self.assert_calls()

    def test_get_image_name(self, cloud=None):
        cloud = cloud or self.cloud
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'image', append=['images'], base_url_append='v2'),
                 json=self.fake_search_return),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'image', append=['images'], base_url_append='v2'),
                 json=self.fake_search_return),
        ])

        self.assertEqual(
            self.image_name, cloud.get_image_name(self.image_id))
        self.assertEqual(
            self.image_name, cloud.get_image_name(self.image_name))

        self.assert_calls()

    def test_get_image_by_id(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'image', append=['images', self.image_id],
                     base_url_append='v2'),
                 json=self.fake_image_dict)
        ])
        self.assertEqual(
            self.cloud._normalize_image(self.fake_image_dict),
            self.cloud.get_image_by_id(self.image_id))
        self.assert_calls()

    def test_get_image_id(self, cloud=None):
        cloud = cloud or self.cloud
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'image', append=['images'], base_url_append='v2'),
                 json=self.fake_search_return),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'image', append=['images'], base_url_append='v2'),
                 json=self.fake_search_return),
        ])

        self.assertEqual(
            self.image_id, cloud.get_image_id(self.image_id))
        self.assertEqual(
            self.image_id, cloud.get_image_id(self.image_name))

        self.assert_calls()

    def test_get_image_name_operator(self):
        # This should work the same as non-operator, just verifying it does.
        self.test_get_image_name(cloud=self.cloud)

    def test_get_image_id_operator(self):
        # This should work the same as the other test, just verifying it does.
        self.test_get_image_id(cloud=self.cloud)

    def test_empty_list_images(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'image', append=['images'], base_url_append='v2'),
                 json={'images': []})
        ])
        self.assertEqual([], self.cloud.list_images())
        self.assert_calls()

    def test_list_images(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'image', append=['images'], base_url_append='v2'),
                 json=self.fake_search_return)
        ])
        self.assertEqual(
            self.cloud._normalize_images([self.fake_image_dict]),
            self.cloud.list_images())
        self.assert_calls()

    def test_list_images_show_all(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'image', append=['images'], base_url_append='v2',
                     qs_elements=['member_status=all']),
                 json=self.fake_search_return)
        ])
        self.assertEqual(
            self.cloud._normalize_images([self.fake_image_dict]),
            self.cloud.list_images(show_all=True))
        self.assert_calls()

    def test_list_images_show_all_deleted(self):
        deleted_image = self.fake_image_dict.copy()
        deleted_image['status'] = 'deleted'
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'image', append=['images'], base_url_append='v2',
                     qs_elements=['member_status=all']),
                 json={'images': [self.fake_image_dict, deleted_image]})
        ])
        self.assertEqual(
            self.cloud._normalize_images([
                self.fake_image_dict, deleted_image]),
            self.cloud.list_images(show_all=True))
        self.assert_calls()

    def test_list_images_no_filter_deleted(self):
        deleted_image = self.fake_image_dict.copy()
        deleted_image['status'] = 'deleted'
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'image', append=['images'], base_url_append='v2'),
                 json={'images': [self.fake_image_dict, deleted_image]})
        ])
        self.assertEqual(
            self.cloud._normalize_images([
                self.fake_image_dict, deleted_image]),
            self.cloud.list_images(filter_deleted=False))
        self.assert_calls()

    def test_list_images_filter_deleted(self):
        deleted_image = self.fake_image_dict.copy()
        deleted_image['status'] = 'deleted'
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'image', append=['images'], base_url_append='v2'),
                 json={'images': [self.fake_image_dict, deleted_image]})
        ])
        self.assertEqual(
            self.cloud._normalize_images([self.fake_image_dict]),
            self.cloud.list_images())
        self.assert_calls()

    def test_list_images_string_properties(self):
        image_dict = self.fake_image_dict.copy()
        image_dict['properties'] = 'list,of,properties'
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'image', append=['images'], base_url_append='v2'),
                 json={'images': [image_dict]}),
        ])
        images = self.cloud.list_images()
        self.assertEqual(
            self.cloud._normalize_images([image_dict]),
            images)
        self.assertEqual(
            images[0]['properties']['properties'],
            'list,of,properties')
        self.assert_calls()

    def test_list_images_paginated(self):
        marker = str(uuid.uuid4())
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'image', append=['images'], base_url_append='v2'),
                 json={'images': [self.fake_image_dict],
                       'next': '/v2/images?marker={marker}'.format(
                           marker=marker)}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'image', append=['images'], base_url_append='v2',
                     qs_elements=['marker={marker}'.format(marker=marker)]),
                 json=self.fake_search_return)
        ])
        self.assertEqual(
            self.cloud._normalize_images([
                self.fake_image_dict, self.fake_image_dict]),
            self.cloud.list_images())
        self.assert_calls()

    def test_create_image_put_v2(self):
        self.cloud.image_api_use_tasks = False

        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'image', append=['images'], base_url_append='v2'),
                 json={'images': []}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'image', append=['images'], base_url_append='v2'),
                 json=self.fake_image_dict,
                 validate=dict(
                     json={
                         u'container_format': u'bare',
                         u'disk_format': u'qcow2',
                         u'name': self.image_name,
                         u'owner_specified.openstack.md5': fakes.NO_MD5,
                         u'owner_specified.openstack.object': self.object_name,
                         u'owner_specified.openstack.sha256': fakes.NO_SHA256,
                         u'visibility': u'private'})
                 ),
            dict(method='PUT',
                 uri=self.get_mock_url(
                     'image', append=['images', self.image_id, 'file'],
                     base_url_append='v2'),
                 request_headers={'Content-Type': 'application/octet-stream'}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'image', append=['images'], base_url_append='v2'),
                 json=self.fake_search_return)
        ])

        self.cloud.create_image(
            self.image_name, self.imagefile.name, wait=True, timeout=1,
            is_public=False)

        self.assert_calls()
        self.assertEqual(self.adapter.request_history[5].text.read(), b'\x00')

    def test_create_image_task(self):
        self.cloud.image_api_use_tasks = True
        endpoint = self.cloud._object_store_client.get_endpoint()

        task_id = str(uuid.uuid4())
        args = dict(
            id=task_id,
            status='success',
            type='import',
            result={
                'image_id': self.image_id,
            },
        )

        image_no_checksums = self.fake_image_dict.copy()
        del(image_no_checksums['owner_specified.openstack.md5'])
        del(image_no_checksums['owner_specified.openstack.sha256'])
        del(image_no_checksums['owner_specified.openstack.object'])

        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'image', append=['images'], base_url_append='v2'),
                 json={'images': []}),
            dict(method='GET',
                 # This is explicitly not using get_mock_url because that
                 # gets us a project-id oriented URL.
                 uri='https://object-store.example.com/info',
                 json=dict(
                     swift={'max_file_size': 1000},
                     slo={'min_segment_size': 500})),
            dict(method='HEAD',
                 uri='{endpoint}/{container}'.format(
                     endpoint=endpoint, container=self.container_name),
                 status_code=404),
            dict(method='PUT',
                 uri='{endpoint}/{container}'.format(
                     endpoint=endpoint, container=self.container_name),
                 status_code=201,
                 headers={'Date': 'Fri, 16 Dec 2016 18:21:20 GMT',
                          'Content-Length': '0',
                          'Content-Type': 'text/html; charset=UTF-8'}),
            dict(method='HEAD',
                 uri='{endpoint}/{container}'.format(
                     endpoint=endpoint, container=self.container_name),
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
                     endpoint=endpoint, container=self.container_name,
                     object=self.image_name),
                 status_code=404),
            dict(method='PUT',
                 uri='{endpoint}/{container}/{object}'.format(
                     endpoint=endpoint, container=self.container_name,
                     object=self.image_name),
                 status_code=201,
                 validate=dict(
                     headers={'x-object-meta-x-sdk-md5': fakes.NO_MD5,
                              'x-object-meta-x-sdk-sha256': fakes.NO_SHA256})
                 ),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'image', append=['images'], base_url_append='v2'),
                 json={'images': []}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'image', append=['tasks'], base_url_append='v2'),
                 json=args,
                 validate=dict(
                     json=dict(
                         type='import', input={
                             'import_from': '{container}/{object}'.format(
                                 container=self.container_name,
                                 object=self.image_name),
                             'image_properties': {'name': self.image_name}}))
                 ),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'image', append=['tasks', task_id], base_url_append='v2'),
                 status_code=503, text='Random error'),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'image', append=['tasks', task_id], base_url_append='v2'),
                 json=args),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'image', append=['images'], base_url_append='v2'),
                 json={'images': [image_no_checksums]}),
            dict(method='PATCH',
                 uri=self.get_mock_url(
                     'image', append=['images', self.image_id],
                     base_url_append='v2'),
                 validate=dict(
                     json=sorted([
                         {u'op': u'add',
                          u'value': '{container}/{object}'.format(
                              container=self.container_name,
                              object=self.image_name),
                          u'path': u'/owner_specified.openstack.object'},
                         {u'op': u'add', u'value': fakes.NO_MD5,
                          u'path': u'/owner_specified.openstack.md5'},
                         {u'op': u'add', u'value': fakes.NO_SHA256,
                          u'path': u'/owner_specified.openstack.sha256'}],
                         key=operator.itemgetter('value')),
                     headers={
                         'Content-Type':
                             'application/openstack-images-v2.1-json-patch'})
                 ),
            dict(method='HEAD',
                 uri='{endpoint}/{container}/{object}'.format(
                     endpoint=endpoint, container=self.container_name,
                     object=self.image_name),
                 headers={
                     'X-Timestamp': '1429036140.50253',
                     'X-Trans-Id': 'txbbb825960a3243b49a36f-005a0dadaedfw1',
                     'Content-Length': '1290170880',
                     'Last-Modified': 'Tue, 14 Apr 2015 18:29:01 GMT',
                     'X-Object-Meta-X-Sdk-Sha256': fakes.NO_SHA256,
                     'X-Object-Meta-X-Sdk-Md5': fakes.NO_MD5,
                     'Date': 'Thu, 16 Nov 2017 15:24:30 GMT',
                     'Accept-Ranges': 'bytes',
                     'Content-Type': 'application/octet-stream',
                     'Etag': fakes.NO_MD5}),
            dict(method='DELETE',
                 uri='{endpoint}/{container}/{object}'.format(
                     endpoint=endpoint, container=self.container_name,
                     object=self.image_name)),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'image', append=['images'], base_url_append='v2'),
                 json=self.fake_search_return)
        ])

        self.cloud.create_image(
            self.image_name, self.imagefile.name, wait=True, timeout=1,
            is_public=False, container=self.container_name)

        self.assert_calls()

    def test_delete_autocreated_no_tasks(self):
        self.use_nothing()
        self.cloud.image_api_use_tasks = False
        deleted = self.cloud.delete_autocreated_image_objects(
            container=self.container_name)
        self.assertFalse(deleted)
        self.assert_calls()

    def test_delete_autocreated_image_objects(self):
        self.use_keystone_v3()
        self.cloud.image_api_use_tasks = True
        endpoint = self.cloud._object_store_client.get_endpoint()
        other_image = self.getUniqueString('no-delete')

        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     service_type='object-store',
                     resource=self.container_name,
                     qs_elements=['format=json']),
                 json=[{
                     'content_type': 'application/octet-stream',
                     'bytes': 1437258240,
                     'hash': '249219347276c331b87bf1ac2152d9af',
                     'last_modified': '2015-02-16T17:50:05.289600',
                     'name': other_image,
                 }, {
                     'content_type': 'application/octet-stream',
                     'bytes': 1290170880,
                     'hash': fakes.NO_MD5,
                     'last_modified': '2015-04-14T18:29:00.502530',
                     'name': self.image_name,
                 }]),
            dict(method='HEAD',
                 uri=self.get_mock_url(
                     service_type='object-store',
                     resource=self.container_name,
                     append=[other_image]),
                 headers={
                     'X-Timestamp': '1429036140.50253',
                     'X-Trans-Id': 'txbbb825960a3243b49a36f-005a0dadaedfw1',
                     'Content-Length': '1290170880',
                     'Last-Modified': 'Tue, 14 Apr 2015 18:29:01 GMT',
                     'X-Object-Meta-X-Shade-Sha256': 'does not matter',
                     'X-Object-Meta-X-Shade-Md5': 'does not matter',
                     'Date': 'Thu, 16 Nov 2017 15:24:30 GMT',
                     'Accept-Ranges': 'bytes',
                     'Content-Type': 'application/octet-stream',
                     'Etag': '249219347276c331b87bf1ac2152d9af',
                 }),
            dict(method='HEAD',
                 uri=self.get_mock_url(
                     service_type='object-store',
                     resource=self.container_name,
                     append=[self.image_name]),
                 headers={
                     'X-Timestamp': '1429036140.50253',
                     'X-Trans-Id': 'txbbb825960a3243b49a36f-005a0dadaedfw1',
                     'Content-Length': '1290170880',
                     'Last-Modified': 'Tue, 14 Apr 2015 18:29:01 GMT',
                     'X-Object-Meta-X-Shade-Sha256': fakes.NO_SHA256,
                     'X-Object-Meta-X-Shade-Md5': fakes.NO_MD5,
                     'Date': 'Thu, 16 Nov 2017 15:24:30 GMT',
                     'Accept-Ranges': 'bytes',
                     'Content-Type': 'application/octet-stream',
                     openstackcloud.OBJECT_AUTOCREATE_KEY: 'true',
                     'Etag': fakes.NO_MD5}),
            dict(method='DELETE',
                 uri='{endpoint}/{container}/{object}'.format(
                     endpoint=endpoint, container=self.container_name,
                     object=self.image_name)),
        ])

        deleted = self.cloud.delete_autocreated_image_objects(
            container=self.container_name)
        self.assertTrue(deleted)

        self.assert_calls()

    def _image_dict(self, fake_image):
        return self.cloud._normalize_image(meta.obj_to_munch(fake_image))

    def _munch_images(self, fake_image):
        return self.cloud._normalize_images([fake_image])

    def _call_create_image(self, name, **kwargs):
        imagefile = tempfile.NamedTemporaryFile(delete=False)
        imagefile.write(b'\0')
        imagefile.close()
        self.cloud.create_image(
            name, imagefile.name, wait=True, timeout=1,
            is_public=False, **kwargs)

    # TODO(shade) Migrate this to requests-mock
    @mock.patch.object(openstack.cloud.OpenStackCloud, '_is_client_version')
    @mock.patch.object(openstack.cloud.OpenStackCloud, '_image_client')
    def test_create_image_put_v1(
            self, mock_image_client, mock_is_client_version):
        mock_is_client_version.return_value = False
        mock_image_client.get.return_value = []
        self.assertEqual([], self.cloud.list_images())

        args = {'name': '42 name',
                'container_format': 'bare', 'disk_format': 'qcow2',
                'properties': {
                    'owner_specified.openstack.md5': mock.ANY,
                    'owner_specified.openstack.sha256': mock.ANY,
                    'owner_specified.openstack.object': 'images/42 name',
                    'is_public': False}}
        ret = munch.Munch(args.copy())
        ret['id'] = '42'
        ret['status'] = 'success'
        mock_image_client.get.side_effect = [
            [],
            [ret],
            [ret],
        ]
        mock_image_client.post.return_value = ret
        mock_image_client.put.return_value = ret
        self._call_create_image('42 name')
        mock_image_client.post.assert_called_with('/images', json=args)
        mock_image_client.put.assert_called_with(
            '/images/42', data=mock.ANY,
            headers={
                'x-image-meta-checksum': mock.ANY,
                'x-glance-registry-purge-props': 'false'
            })
        mock_image_client.get.assert_called_with('/images/detail', params={})
        self.assertEqual(
            self._munch_images(ret), self.cloud.list_images())

    # TODO(shade) Migrate this to requests-mock
    @mock.patch.object(openstack.cloud.OpenStackCloud, '_is_client_version')
    @mock.patch.object(openstack.cloud.OpenStackCloud, '_image_client')
    def test_create_image_put_v1_bad_delete(
            self, mock_image_client, mock_is_client_version):
        mock_is_client_version.return_value = False
        mock_image_client.get.return_value = []
        self.assertEqual([], self.cloud.list_images())

        args = {'name': '42 name',
                'container_format': 'bare', 'disk_format': 'qcow2',
                'properties': {
                    'owner_specified.openstack.md5': mock.ANY,
                    'owner_specified.openstack.sha256': mock.ANY,
                    'owner_specified.openstack.object': 'images/42 name',
                    'is_public': False}}
        ret = munch.Munch(args.copy())
        ret['id'] = '42'
        ret['status'] = 'success'
        mock_image_client.get.side_effect = [
            [],
            [ret],
        ]
        mock_image_client.post.return_value = ret
        mock_image_client.put.side_effect = exc.OpenStackCloudHTTPError(
            "Some error")
        self.assertRaises(
            exc.OpenStackCloudHTTPError,
            self._call_create_image,
            '42 name')
        mock_image_client.post.assert_called_with('/images', json=args)
        mock_image_client.put.assert_called_with(
            '/images/42', data=mock.ANY,
            headers={
                'x-image-meta-checksum': mock.ANY,
                'x-glance-registry-purge-props': 'false'
            })
        mock_image_client.delete.assert_called_with('/images/42')

    # TODO(shade) Migrate this to requests-mock
    @mock.patch.object(openstack.cloud.OpenStackCloud, '_is_client_version')
    @mock.patch.object(openstack.cloud.OpenStackCloud, '_image_client')
    def test_update_image_no_patch(
            self, mock_image_client, mock_is_client_version):
        mock_is_client_version.return_value = True
        self.cloud.image_api_use_tasks = False

        mock_image_client.get.return_value = []
        self.assertEqual([], self.cloud.list_images())

        args = {'name': '42 name',
                'container_format': 'bare', 'disk_format': 'qcow2',
                'owner_specified.openstack.md5': mock.ANY,
                'owner_specified.openstack.sha256': mock.ANY,
                'owner_specified.openstack.object': 'images/42 name',
                'visibility': 'private',
                'min_disk': 0, 'min_ram': 0}
        ret = munch.Munch(args.copy())
        ret['id'] = '42'
        ret['status'] = 'success'
        mock_image_client.get.side_effect = [
            [],
            [ret],
            [ret],
        ]
        self.cloud.update_image_properties(
            image=self._image_dict(ret),
            **{'owner_specified.openstack.object': 'images/42 name'})
        mock_image_client.get.assert_called_with('/images', params={})
        mock_image_client.patch.assert_not_called()

    # TODO(shade) Migrate this to requests-mock
    @mock.patch.object(openstack.cloud.OpenStackCloud, '_is_client_version')
    @mock.patch.object(openstack.cloud.OpenStackCloud, '_image_client')
    def test_create_image_put_v2_bad_delete(
            self, mock_image_client, mock_is_client_version):
        mock_is_client_version.return_value = True
        self.cloud.image_api_use_tasks = False

        mock_image_client.get.return_value = []
        self.assertEqual([], self.cloud.list_images())

        args = {'name': '42 name',
                'container_format': 'bare', 'disk_format': 'qcow2',
                'owner_specified.openstack.md5': mock.ANY,
                'owner_specified.openstack.sha256': mock.ANY,
                'owner_specified.openstack.object': 'images/42 name',
                'visibility': 'private',
                'min_disk': 0, 'min_ram': 0}
        ret = munch.Munch(args.copy())
        ret['id'] = '42'
        ret['status'] = 'success'
        mock_image_client.get.side_effect = [
            [],
            [ret],
            [ret],
        ]
        mock_image_client.post.return_value = ret
        mock_image_client.put.side_effect = exc.OpenStackCloudHTTPError(
            "Some error")
        self.assertRaises(
            exc.OpenStackCloudHTTPError,
            self._call_create_image,
            '42 name', min_disk='0', min_ram=0)
        mock_image_client.post.assert_called_with('/images', json=args)
        mock_image_client.put.assert_called_with(
            '/images/42/file',
            headers={'Content-Type': 'application/octet-stream'},
            data=mock.ANY)
        mock_image_client.delete.assert_called_with('/images/42')

    # TODO(shade) Migrate this to requests-mock
    @mock.patch.object(openstack.cloud.OpenStackCloud, '_is_client_version')
    @mock.patch.object(openstack.cloud.OpenStackCloud, '_image_client')
    def test_create_image_put_bad_int(
            self, mock_image_client, mock_is_client_version):
        mock_is_client_version.return_value = True
        self.cloud.image_api_use_tasks = False

        self.assertRaises(
            exc.OpenStackCloudException,
            self._call_create_image, '42 name', min_disk='fish', min_ram=0)
        mock_image_client.post.assert_not_called()

    # TODO(shade) Migrate this to requests-mock
    @mock.patch.object(openstack.cloud.OpenStackCloud, '_is_client_version')
    @mock.patch.object(openstack.cloud.OpenStackCloud, '_image_client')
    def test_create_image_put_user_int(
            self, mock_image_client, mock_is_client_version):
        mock_is_client_version.return_value = True
        self.cloud.image_api_use_tasks = False

        args = {'name': '42 name',
                'container_format': 'bare', 'disk_format': u'qcow2',
                'owner_specified.openstack.md5': mock.ANY,
                'owner_specified.openstack.sha256': mock.ANY,
                'owner_specified.openstack.object': 'images/42 name',
                'int_v': '12345',
                'visibility': 'private',
                'min_disk': 0, 'min_ram': 0}
        ret = munch.Munch(args.copy())
        ret['id'] = '42'
        ret['status'] = 'success'
        mock_image_client.get.side_effect = [
            [],
            [ret],
            [ret]
        ]
        mock_image_client.post.return_value = ret
        self._call_create_image(
            '42 name', min_disk='0', min_ram=0, int_v=12345)
        mock_image_client.post.assert_called_with('/images', json=args)
        mock_image_client.put.assert_called_with(
            '/images/42/file',
            headers={'Content-Type': 'application/octet-stream'},
            data=mock.ANY)
        mock_image_client.get.assert_called_with('/images', params={})
        self.assertEqual(
            self._munch_images(ret), self.cloud.list_images())

    # TODO(shade) Migrate this to requests-mock
    @mock.patch.object(openstack.cloud.OpenStackCloud, '_is_client_version')
    @mock.patch.object(openstack.cloud.OpenStackCloud, '_image_client')
    def test_create_image_put_meta_int(
            self, mock_image_client, mock_is_client_version):
        mock_is_client_version.return_value = True
        self.cloud.image_api_use_tasks = False

        mock_image_client.get.return_value = []
        self.assertEqual([], self.cloud.list_images())

        self._call_create_image(
            '42 name', min_disk='0', min_ram=0, meta={'int_v': 12345})
        args = {'name': '42 name',
                'container_format': 'bare', 'disk_format': u'qcow2',
                'owner_specified.openstack.md5': mock.ANY,
                'owner_specified.openstack.sha256': mock.ANY,
                'owner_specified.openstack.object': 'images/42 name',
                'int_v': 12345,
                'visibility': 'private',
                'min_disk': 0, 'min_ram': 0}
        ret = munch.Munch(args.copy())
        ret['id'] = '42'
        ret['status'] = 'success'
        mock_image_client.get.return_value = [ret]
        mock_image_client.post.return_value = ret
        mock_image_client.get.assert_called_with('/images', params={})
        self.assertEqual(
            self._munch_images(ret), self.cloud.list_images())

    # TODO(shade) Migrate this to requests-mock
    @mock.patch.object(openstack.cloud.OpenStackCloud, '_is_client_version')
    @mock.patch.object(openstack.cloud.OpenStackCloud, '_image_client')
    def test_create_image_put_protected(
            self, mock_image_client, mock_is_client_version):
        mock_is_client_version.return_value = True
        self.cloud.image_api_use_tasks = False

        mock_image_client.get.return_value = []
        self.assertEqual([], self.cloud.list_images())

        args = {'name': '42 name',
                'container_format': 'bare', 'disk_format': u'qcow2',
                'owner_specified.openstack.md5': mock.ANY,
                'owner_specified.openstack.sha256': mock.ANY,
                'owner_specified.openstack.object': 'images/42 name',
                'protected': False,
                'int_v': '12345',
                'visibility': 'private',
                'min_disk': 0, 'min_ram': 0}
        ret = munch.Munch(args.copy())
        ret['id'] = '42'
        ret['status'] = 'success'
        mock_image_client.get.side_effect = [
            [],
            [ret],
            [ret],
        ]
        mock_image_client.put.return_value = ret
        mock_image_client.post.return_value = ret
        self._call_create_image(
            '42 name', min_disk='0', min_ram=0, properties={'int_v': 12345},
            protected=False)
        mock_image_client.post.assert_called_with('/images', json=args)
        mock_image_client.put.assert_called_with(
            '/images/42/file', data=mock.ANY,
            headers={'Content-Type': 'application/octet-stream'})
        self.assertEqual(self._munch_images(ret), self.cloud.list_images())

    # TODO(shade) Migrate this to requests-mock
    @mock.patch.object(openstack.cloud.OpenStackCloud, '_is_client_version')
    @mock.patch.object(openstack.cloud.OpenStackCloud, '_image_client')
    def test_create_image_put_user_prop(
            self, mock_image_client, mock_is_client_version):
        mock_is_client_version.return_value = True
        self.cloud.image_api_use_tasks = False

        mock_image_client.get.return_value = []
        self.assertEqual([], self.cloud.list_images())

        args = {'name': '42 name',
                'container_format': 'bare', 'disk_format': u'qcow2',
                'owner_specified.openstack.md5': mock.ANY,
                'owner_specified.openstack.sha256': mock.ANY,
                'owner_specified.openstack.object': 'images/42 name',
                'int_v': '12345',
                'xenapi_use_agent': 'False',
                'visibility': 'private',
                'min_disk': 0, 'min_ram': 0}
        ret = munch.Munch(args.copy())
        ret['id'] = '42'
        ret['status'] = 'success'
        mock_image_client.get.return_value = [ret]
        mock_image_client.post.return_value = ret
        self._call_create_image(
            '42 name', min_disk='0', min_ram=0, properties={'int_v': 12345})
        mock_image_client.get.assert_called_with('/images', params={})
        self.assertEqual(
            self._munch_images(ret), self.cloud.list_images())


class TestImageSuburl(BaseTestImage):

    def setUp(self):
        super(TestImageSuburl, self).setUp()
        self.use_keystone_v3(catalog='catalog-v3-suburl.json')
        self.use_glance(
            image_version_json='image-version-suburl.json',
            image_discovery_url='https://example.com/image')

    def test_list_images(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'image', append=['images'], base_url_append='v2'),
                 json=self.fake_search_return)
        ])
        self.assertEqual(
            self.cloud._normalize_images([self.fake_image_dict]),
            self.cloud.list_images())
        self.assert_calls()

    def test_list_images_paginated(self):
        marker = str(uuid.uuid4())
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'image', append=['images'], base_url_append='v2'),
                 json={'images': [self.fake_image_dict],
                       'next': '/v2/images?marker={marker}'.format(
                           marker=marker)}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'image', append=['images'], base_url_append='v2',
                     qs_elements=['marker={marker}'.format(marker=marker)]),
                 json=self.fake_search_return)
        ])
        self.assertEqual(
            self.cloud._normalize_images([
                self.fake_image_dict, self.fake_image_dict]),
            self.cloud.list_images())
        self.assert_calls()


class TestImageV1Only(base.TestCase):

    def setUp(self):
        super(TestImageV1Only, self).setUp()
        self.use_glance(image_version_json='image-version-v1.json')

    def test_config_v1(self):

        self.cloud.config.config['image_api_version'] = '1'
        # We override the scheme of the endpoint with the scheme of the service
        # because glance has a bug where it doesn't return https properly.
        self.assertEqual(
            'https://image.example.com/v1/',
            self.cloud._image_client.get_endpoint())
        self.assertTrue(self.cloud._is_client_version('image', 1))

    def test_config_v2(self):
        self.cloud.config.config['image_api_version'] = '2'
        # We override the scheme of the endpoint with the scheme of the service
        # because glance has a bug where it doesn't return https properly.
        self.assertEqual(
            'https://image.example.com/v1/',
            self.cloud._image_client.get_endpoint())
        self.assertFalse(self.cloud._is_client_version('image', 2))


class TestImageV2Only(base.TestCase):

    def setUp(self):
        super(TestImageV2Only, self).setUp()
        self.use_glance(image_version_json='image-version-v2.json')

    def test_config_v1(self):
        self.cloud.config.config['image_api_version'] = '1'
        # We override the scheme of the endpoint with the scheme of the service
        # because glance has a bug where it doesn't return https properly.
        self.assertEqual(
            'https://image.example.com/v2/',
            self.cloud._image_client.get_endpoint())
        self.assertTrue(self.cloud._is_client_version('image', 2))

    def test_config_v2(self):
        self.cloud.config.config['image_api_version'] = '2'
        # We override the scheme of the endpoint with the scheme of the service
        # because glance has a bug where it doesn't return https properly.
        self.assertEqual(
            'https://image.example.com/v2/',
            self.cloud._image_client.get_endpoint())
        self.assertTrue(self.cloud._is_client_version('image', 2))


class TestImageVolume(BaseTestImage):

    def setUp(self):
        super(TestImageVolume, self).setUp()
        self.volume_id = str(uuid.uuid4())

    def test_create_image_volume(self):

        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(
                     'volumev2', append=['volumes', self.volume_id, 'action']),
                 json={'os-volume_upload_image': {'image_id': self.image_id}},
                 validate=dict(json={
                     u'os-volume_upload_image': {
                         u'container_format': u'bare',
                         u'disk_format': u'qcow2',
                         u'force': False,
                         u'image_name': u'fake_image'}})
                 ),
            # NOTE(notmorgan): Glance discovery happens here, insert the
            # glance discovery mock at this point, DO NOT use the
            # .use_glance() method, that is intended only for use in
            # .setUp
            self.get_glance_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'image', append=['images'], base_url_append='v2'),
                 json=self.fake_search_return)
        ])

        self.cloud.create_image(
            'fake_image', self.imagefile.name, wait=True, timeout=1,
            volume={'id': self.volume_id})

        self.assert_calls()

    def test_create_image_volume_duplicate(self):

        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(
                     'volumev2', append=['volumes', self.volume_id, 'action']),
                 json={'os-volume_upload_image': {'image_id': self.image_id}},
                 validate=dict(json={
                     u'os-volume_upload_image': {
                         u'container_format': u'bare',
                         u'disk_format': u'qcow2',
                         u'force': True,
                         u'image_name': u'fake_image'}})
                 ),
            # NOTE(notmorgan): Glance discovery happens here, insert the
            # glance discovery mock at this point, DO NOT use the
            # .use_glance() method, that is intended only for use in
            # .setUp
            self.get_glance_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'image', append=['images'], base_url_append='v2'),
                 json=self.fake_search_return)
        ])

        self.cloud.create_image(
            'fake_image', self.imagefile.name, wait=True, timeout=1,
            volume={'id': self.volume_id}, allow_duplicates=True)

        self.assert_calls()


class TestImageBrokenDiscovery(base.TestCase):

    def setUp(self):
        super(TestImageBrokenDiscovery, self).setUp()
        self.use_glance(image_version_json='image-version-broken.json')

    def test_url_fix(self):
        # image-version-broken.json has both http urls and localhost as the
        # host. This is testing that what is discovered is https, because
        # that's what's in the catalog, and image.example.com for the same
        # reason.
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'image', append=['images'], base_url_append='v2'),
                 json={'images': []})
        ])
        self.assertEqual([], self.cloud.list_images())
        self.assertEqual(
            self.cloud._image_client.get_endpoint(),
            'https://image.example.com/v2/')
        self.assert_calls()
