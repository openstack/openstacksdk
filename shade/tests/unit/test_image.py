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

import operator
import tempfile
import uuid

import mock
import munch
import os_client_config as occ
import six

import shade
from shade import exc
from shade import meta
from shade.tests.unit import base


NO_MD5 = '93b885adfe0da089cdf634904fd59f71'
NO_SHA256 = '6e340b9cffb37a989ca544e6bb780a2c78901d3fb33738768511a30617afa01d'
CINDER_URL = 'https://volume.example.com/v2/1c36b64c840a42cd9e9b931a369337f0'


class BaseTestImage(base.RequestsMockTestCase):

    def setUp(self):
        super(BaseTestImage, self).setUp()
        self.image_id = str(uuid.uuid4())
        self.imagefile = tempfile.NamedTemporaryFile(delete=False)
        self.imagefile.write(b'\0')
        self.imagefile.close()
        self.fake_image_dict = {
            u'image_state': u'available',
            u'container_format': u'bare',
            u'min_ram': 0,
            u'ramdisk_id': None,
            u'updated_at': u'2016-02-10T05:05:02Z',
            u'file': '/v2/images/' + self.image_id + '/file',
            u'size': 3402170368,
            u'image_type': u'snapshot',
            u'disk_format': u'qcow2',
            u'id': self.image_id,
            u'schema': u'/v2/schemas/image',
            u'status': u'active',
            u'tags': [],
            u'visibility': u'private',
            u'locations': [{
                u'url': u'http://127.0.0.1/images/' + self.image_id,
                u'metadata': {}}],
            u'min_disk': 40,
            u'virtual_size': None,
            u'name': u'fake_image',
            u'checksum': u'ee36e35a297980dee1b514de9803ec6d',
            u'created_at': u'2016-02-10T05:03:11Z',
            u'owner_specified.shade.md5': NO_MD5,
            u'owner_specified.shade.sha256': NO_SHA256,
            u'owner_specified.shade.object': 'images/fake_image',
            u'protected': False}
        self.fake_search_return = {'images': [self.fake_image_dict]}
        self.output = uuid.uuid4().bytes


class TestImage(BaseTestImage):

    def setUp(self):
        super(TestImage, self).setUp()
        self.use_glance()

    def test_config_v1(self):
        self.cloud.cloud_config.config['image_api_version'] = '1'
        # We override the scheme of the endpoint with the scheme of the service
        # because glance has a bug where it doesn't return https properly.
        self.assertEqual(
            'https://image.example.com/v1/',
            self.cloud._image_client.get_endpoint())
        self.assertEqual(
            '1', self.cloud_config.get_api_version('image'))

    def test_config_v2(self):
        self.cloud.cloud_config.config['image_api_version'] = '2'
        # We override the scheme of the endpoint with the scheme of the service
        # because glance has a bug where it doesn't return https properly.
        self.assertEqual(
            'https://image.example.com/v2/',
            self.cloud._image_client.get_endpoint())
        self.assertEqual(
            '2', self.cloud_config.get_api_version('image'))

    def test_download_image_no_output(self):
        self.assertRaises(exc.OpenStackCloudException,
                          self.cloud.download_image, 'fake_image')

    def test_download_image_two_outputs(self):
        fake_fd = six.BytesIO()
        self.assertRaises(exc.OpenStackCloudException,
                          self.cloud.download_image, 'fake_image',
                          output_path='fake_path', output_file=fake_fd)

    def test_download_image_no_images_found(self):
        self.register_uri(
            'GET', 'https://image.example.com/v2/images',
            json=dict(images=[]))
        self.assertRaises(exc.OpenStackCloudResourceNotFound,
                          self.cloud.download_image, 'fake_image',
                          output_path='fake_path')
        self.assert_calls()

    def _register_image_mocks(self):
        self.register_uri(
            'GET', 'https://image.example.com/v2/images',
            json=self.fake_search_return)
        self.register_uri(
            'GET', 'https://image.example.com/v2/images/{id}/file'.format(
                id=self.image_id),
            content=self.output,
            headers={
                'Content-Type': 'application/octet-stream'
            })

    def test_download_image_with_fd(self):
        self._register_image_mocks()
        output_file = six.BytesIO()
        self.cloud.download_image('fake_image', output_file=output_file)
        output_file.seek(0)
        self.assertEqual(output_file.read(), self.output)
        self.assert_calls()

    def test_download_image_with_path(self):
        self._register_image_mocks()
        output_file = tempfile.NamedTemporaryFile()
        self.cloud.download_image('fake_image', output_path=output_file.name)
        output_file.seek(0)
        self.assertEqual(output_file.read(), self.output)
        self.assert_calls()

    def test_empty_list_images(self):
        self.register_uri(
            'GET', 'https://image.example.com/v2/images', json={'images': []})
        self.assertEqual([], self.cloud.list_images())
        self.assert_calls()

    def test_list_images(self):
        self.register_uri(
            'GET', 'https://image.example.com/v2/images',
            json=self.fake_search_return)
        self.assertEqual(
            self.cloud._normalize_images([self.fake_image_dict]),
            self.cloud.list_images())
        self.assert_calls()

    def test_list_images_paginated(self):
        marker = str(uuid.uuid4())
        self.register_uri(
            'GET', 'https://image.example.com/v2/images',
            json={
                'images': [self.fake_image_dict],
                'next': '/v2/images?marker={marker}'.format(marker=marker),
            })
        self.register_uri(
            'GET',
            'https://image.example.com/v2/images?marker={marker}'.format(
                marker=marker),
            json=self.fake_search_return)
        self.assertEqual(
            self.cloud._normalize_images([
                self.fake_image_dict, self.fake_image_dict]),
            self.cloud.list_images())
        self.assert_calls()

    def test_create_image_put_v2(self):
        self.cloud.image_api_use_tasks = False

        self.register_uri(
            'GET', 'https://image.example.com/v2/images',
            json={'images': []})

        self.register_uri(
            'POST', 'https://image.example.com/v2/images',
            json=self.fake_image_dict,
            validate=dict(
                json={
                    u'container_format': u'bare',
                    u'disk_format': u'qcow2',
                    u'name': u'fake_image',
                    u'owner_specified.shade.md5': NO_MD5,
                    u'owner_specified.shade.object': u'images/fake_image',
                    u'owner_specified.shade.sha256': NO_SHA256,
                    u'visibility': u'private'
                }),
        )
        self.register_uri(
            'PUT', 'https://image.example.com/v2/images/{id}/file'.format(
                id=self.image_id),
            request_headers={'Content-Type': 'application/octet-stream'})

        self.register_uri(
            'GET', 'https://image.example.com/v2/images',
            json=self.fake_search_return)

        self.cloud.create_image(
            'fake_image', self.imagefile.name, wait=True, timeout=1,
            is_public=False)

        self.assert_calls()
        self.assertEqual(self.adapter.request_history[5].text.read(), b'\x00')

    def test_create_image_task(self):
        self.cloud.image_api_use_tasks = True
        image_name = 'name-99'
        container_name = 'image_upload_v2_test_container'
        endpoint = self.cloud._object_store_client.get_endpoint()

        self.register_uri(
            'GET', 'https://image.example.com/v2/images', json={'images': []})

        self.register_uri(
            'GET', 'https://object-store.example.com/info',
            json=dict(
                swift={'max_file_size': 1000},
                slo={'min_segment_size': 500}))

        self.register_uri(
            'HEAD', '{endpoint}/{container}'.format(
                endpoint=endpoint,
                container=container_name),
            status_code=404)

        self.register_uri(
            'PUT', '{endpoint}/{container}'.format(
                endpoint=endpoint,
                container=container_name,),
            status_code=201,
            headers={
                'Date': 'Fri, 16 Dec 2016 18:21:20 GMT',
                'Content-Length': '0',
                'Content-Type': 'text/html; charset=UTF-8',
            })

        self.register_uri(
            'HEAD', '{endpoint}/{container}'.format(
                endpoint=endpoint,
                container=container_name),
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

        self.register_uri(
            'HEAD', '{endpoint}/{container}/{object}'.format(
                endpoint=endpoint,
                container=container_name, object=image_name),
            status_code=404)

        self.register_uri(
            'PUT', '{endpoint}/{container}/{object}'.format(
                endpoint=endpoint,
                container=container_name, object=image_name),
            status_code=201,
            validate=dict(
                headers={
                    'x-object-meta-x-shade-md5': NO_MD5,
                    'x-object-meta-x-shade-sha256': NO_SHA256,
                }))

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
        del(image_no_checksums['owner_specified.shade.md5'])
        del(image_no_checksums['owner_specified.shade.sha256'])
        del(image_no_checksums['owner_specified.shade.object'])

        self.register_uri(
            'GET', 'https://image.example.com/v2/images',
            json={'images': []})

        self.register_uri(
            'POST', 'https://image.example.com/v2/tasks',
            json=args,
            validate=dict(
                json=dict(
                    type='import', input={
                        'import_from': '{container}/{object}'.format(
                            container=container_name, object=image_name),
                        'image_properties': {'name': image_name}})))

        self.register_uri(
            'GET',
            'https://image.example.com/v2/tasks/{id}'.format(id=task_id),
            status_code=503, text='Random error')

        self.register_uri(
            'GET',
            'https://image.example.com/v2/tasks/{id}'.format(id=task_id),
            json={'images': args})

        self.register_uri(
            'GET', 'https://image.example.com/v2/images',
            json={'images': [image_no_checksums]})

        self.register_uri(
            'PATCH',
            'https://image.example.com/v2/images/{id}'.format(
                id=self.image_id),
            validate=dict(
                json=sorted([
                    {
                        u'op': u'add',
                        u'value': '{container}/{object}'.format(
                            container=container_name, object=image_name),
                        u'path': u'/owner_specified.shade.object'
                    }, {
                        u'op': u'add',
                        u'value': NO_MD5,
                        u'path': u'/owner_specified.shade.md5'
                    }, {
                        u'op': u'add', u'value': NO_SHA256,
                        u'path': u'/owner_specified.shade.sha256'
                    }], key=operator.itemgetter('value')),
                headers={
                    'Content-Type':
                    'application/openstack-images-v2.1-json-patch'
                }))

        self.register_uri(
            'GET', 'https://image.example.com/v2/images',
            json=self.fake_search_return)

        self.cloud.create_image(
            image_name, self.imagefile.name, wait=True, timeout=1,
            is_public=False, container=container_name)

        self.assert_calls()

    def _image_dict(self, fake_image):
        return self.cloud._normalize_image(meta.obj_to_dict(fake_image))

    def _munch_images(self, fake_image):
        return self.cloud._normalize_images([fake_image])

    def _call_create_image(self, name, **kwargs):
        imagefile = tempfile.NamedTemporaryFile(delete=False)
        imagefile.write(b'\0')
        imagefile.close()
        self.cloud.create_image(
            name, imagefile.name, wait=True, timeout=1,
            is_public=False, **kwargs)

    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, '_image_client')
    def test_create_image_put_v1(self, mock_image_client, mock_api_version):
        mock_api_version.return_value = '1'
        mock_image_client.get.return_value = []
        self.assertEqual([], self.cloud.list_images())

        args = {'name': '42 name',
                'container_format': 'bare', 'disk_format': 'qcow2',
                'properties': {
                    'owner_specified.shade.md5': mock.ANY,
                    'owner_specified.shade.sha256': mock.ANY,
                    'owner_specified.shade.object': 'images/42 name',
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
        mock_image_client.get.assert_called_with('/images/detail')
        self.assertEqual(
            self._munch_images(ret), self.cloud.list_images())

    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, '_image_client')
    def test_create_image_put_v1_bad_delete(
            self, mock_image_client, mock_api_version):
        mock_api_version.return_value = '1'
        mock_image_client.get.return_value = []
        self.assertEqual([], self.cloud.list_images())

        args = {'name': '42 name',
                'container_format': 'bare', 'disk_format': 'qcow2',
                'properties': {
                    'owner_specified.shade.md5': mock.ANY,
                    'owner_specified.shade.sha256': mock.ANY,
                    'owner_specified.shade.object': 'images/42 name',
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
            "Some error", {})
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

    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, '_image_client')
    def test_update_image_no_patch(self, mock_image_client, mock_api_version):
        mock_api_version.return_value = '2'
        self.cloud.image_api_use_tasks = False

        mock_image_client.get.return_value = []
        self.assertEqual([], self.cloud.list_images())

        args = {'name': '42 name',
                'container_format': 'bare', 'disk_format': 'qcow2',
                'owner_specified.shade.md5': mock.ANY,
                'owner_specified.shade.sha256': mock.ANY,
                'owner_specified.shade.object': 'images/42 name',
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
            **{'owner_specified.shade.object': 'images/42 name'})
        mock_image_client.get.assert_called_with('/images')
        mock_image_client.patch.assert_not_called()

    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, '_image_client')
    def test_create_image_put_v2_bad_delete(
            self, mock_image_client, mock_api_version):
        mock_api_version.return_value = '2'
        self.cloud.image_api_use_tasks = False

        mock_image_client.get.return_value = []
        self.assertEqual([], self.cloud.list_images())

        args = {'name': '42 name',
                'container_format': 'bare', 'disk_format': 'qcow2',
                'owner_specified.shade.md5': mock.ANY,
                'owner_specified.shade.sha256': mock.ANY,
                'owner_specified.shade.object': 'images/42 name',
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
            "Some error", {})
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

    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, '_image_client')
    def test_create_image_put_bad_int(
            self, mock_image_client, mock_api_version):
        mock_api_version.return_value = '2'
        self.cloud.image_api_use_tasks = False

        self.assertRaises(
            exc.OpenStackCloudException,
            self._call_create_image, '42 name', min_disk='fish', min_ram=0)
        mock_image_client.post.assert_not_called()

    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, '_image_client')
    def test_create_image_put_user_int(
            self, mock_image_client, mock_api_version):
        mock_api_version.return_value = '2'
        self.cloud.image_api_use_tasks = False

        args = {'name': '42 name',
                'container_format': 'bare', 'disk_format': u'qcow2',
                'owner_specified.shade.md5': mock.ANY,
                'owner_specified.shade.sha256': mock.ANY,
                'owner_specified.shade.object': 'images/42 name',
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
        mock_image_client.get.assert_called_with('/images')
        self.assertEqual(
            self._munch_images(ret), self.cloud.list_images())

    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, '_image_client')
    def test_create_image_put_meta_int(
            self, mock_image_client, mock_api_version):
        mock_api_version.return_value = '2'
        self.cloud.image_api_use_tasks = False

        mock_image_client.get.return_value = []
        self.assertEqual([], self.cloud.list_images())

        self._call_create_image(
            '42 name', min_disk='0', min_ram=0, meta={'int_v': 12345})
        args = {'name': '42 name',
                'container_format': 'bare', 'disk_format': u'qcow2',
                'owner_specified.shade.md5': mock.ANY,
                'owner_specified.shade.sha256': mock.ANY,
                'owner_specified.shade.object': 'images/42 name',
                'int_v': 12345,
                'visibility': 'private',
                'min_disk': 0, 'min_ram': 0}
        ret = munch.Munch(args.copy())
        ret['id'] = '42'
        ret['status'] = 'success'
        mock_image_client.get.return_value = [ret]
        mock_image_client.post.return_value = ret
        mock_image_client.get.assert_called_with('/images')
        self.assertEqual(
            self._munch_images(ret), self.cloud.list_images())

    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, '_image_client')
    def test_create_image_put_protected(
            self, mock_image_client, mock_api_version):
        mock_api_version.return_value = '2'
        self.cloud.image_api_use_tasks = False

        mock_image_client.get.return_value = []
        self.assertEqual([], self.cloud.list_images())

        args = {'name': '42 name',
                'container_format': 'bare', 'disk_format': u'qcow2',
                'owner_specified.shade.md5': mock.ANY,
                'owner_specified.shade.sha256': mock.ANY,
                'owner_specified.shade.object': 'images/42 name',
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

    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, '_image_client')
    def test_create_image_put_user_prop(
            self, mock_image_client, mock_api_version):
        mock_api_version.return_value = '2'
        self.cloud.image_api_use_tasks = False

        mock_image_client.get.return_value = []
        self.assertEqual([], self.cloud.list_images())

        args = {'name': '42 name',
                'container_format': 'bare', 'disk_format': u'qcow2',
                'owner_specified.shade.md5': mock.ANY,
                'owner_specified.shade.sha256': mock.ANY,
                'owner_specified.shade.object': 'images/42 name',
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
        mock_image_client.get.assert_called_with('/images')
        self.assertEqual(
            self._munch_images(ret), self.cloud.list_images())


class TestImageV1Only(base.RequestsMockTestCase):

    def setUp(self):
        super(TestImageV1Only, self).setUp()
        self.use_glance(image_version_json='image-version-v1.json')

    def test_config_v1(self):

        self.cloud.cloud_config.config['image_api_version'] = '1'
        # We override the scheme of the endpoint with the scheme of the service
        # because glance has a bug where it doesn't return https properly.
        self.assertEqual(
            'https://image.example.com/v1/',
            self.cloud._image_client.get_endpoint())
        self.assertEqual(
            '1', self.cloud_config.get_api_version('image'))

    def test_config_v2(self):
        self.cloud.cloud_config.config['image_api_version'] = '2'
        # We override the scheme of the endpoint with the scheme of the service
        # because glance has a bug where it doesn't return https properly.
        self.assertEqual(
            'https://image.example.com/v1/',
            self.cloud._image_client.get_endpoint())
        self.assertEqual(
            '1', self.cloud_config.get_api_version('image'))


class TestImageV2Only(base.RequestsMockTestCase):

    def setUp(self):
        super(TestImageV2Only, self).setUp()
        self.use_glance(image_version_json='image-version-v2.json')

    def test_config_v1(self):
        self.cloud.cloud_config.config['image_api_version'] = '1'
        # We override the scheme of the endpoint with the scheme of the service
        # because glance has a bug where it doesn't return https properly.
        self.assertEqual(
            'https://image.example.com/v2/',
            self.cloud._image_client.get_endpoint())
        self.assertEqual(
            '2', self.cloud_config.get_api_version('image'))

    def test_config_v2(self):
        self.cloud.cloud_config.config['image_api_version'] = '2'
        # We override the scheme of the endpoint with the scheme of the service
        # because glance has a bug where it doesn't return https properly.
        self.assertEqual(
            'https://image.example.com/v2/',
            self.cloud._image_client.get_endpoint())
        self.assertEqual(
            '2', self.cloud_config.get_api_version('image'))


class TestImageVersionDiscovery(BaseTestImage):

    def test_version_discovery_skip(self):
        self.cloud.cloud_config.config['image_endpoint_override'] = \
            'https://image.example.com/v2/override'

        self.register_uri(
            'GET', 'https://image.example.com/v2/override/images',
            json={'images': []})
        self.assertEqual([], self.cloud.list_images())
        self.assertEqual(
            self.cloud._image_client.endpoint_override,
            'https://image.example.com/v2/override')
        self.assert_calls()


class TestImageVolume(BaseTestImage):

    def test_create_image_volume(self):

        volume_id = 'some-volume'

        self.register_uri(
            'POST', '{endpoint}/volumes/{id}/action'.format(
                endpoint=CINDER_URL, id=volume_id),
            json={'os-volume_upload_image': {'image_id': self.image_id}},
            validate=dict(json={
                u'os-volume_upload_image': {
                    u'container_format': u'bare',
                    u'disk_format': u'qcow2',
                    u'force': False,
                    u'image_name': u'fake_image'}}))

        self.use_glance()

        self.register_uri(
            'GET', 'https://image.example.com/v2/images',
            json=self.fake_search_return)

        self.cloud.create_image(
            'fake_image', self.imagefile.name, wait=True, timeout=1,
            volume={'id': volume_id})

        self.assert_calls()

    def test_create_image_volume_duplicate(self):

        volume_id = 'some-volume'

        self.register_uri(
            'POST', '{endpoint}/volumes/{id}/action'.format(
                endpoint=CINDER_URL, id=volume_id),
            json={'os-volume_upload_image': {'image_id': self.image_id}},
            validate=dict(json={
                u'os-volume_upload_image': {
                    u'container_format': u'bare',
                    u'disk_format': u'qcow2',
                    u'force': True,
                    u'image_name': u'fake_image'}}))

        self.use_glance()

        self.register_uri(
            'GET', 'https://image.example.com/v2/images',
            json=self.fake_search_return)

        self.cloud.create_image(
            'fake_image', self.imagefile.name, wait=True, timeout=1,
            volume={'id': volume_id}, allow_duplicates=True)

        self.assert_calls()
