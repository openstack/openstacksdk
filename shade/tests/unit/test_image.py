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


class TestImage(base.RequestsMockTestCase):

    def setUp(self):
        super(TestImage, self).setUp()
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

    def test_download_image_no_output(self):
        self.assertRaises(exc.OpenStackCloudException,
                          self.cloud.download_image, 'fake_image')

    def test_download_image_two_outputs(self):
        fake_fd = six.BytesIO()
        self.assertRaises(exc.OpenStackCloudException,
                          self.cloud.download_image, 'fake_image',
                          output_path='fake_path', output_file=fake_fd)

    def test_download_image_no_images_found(self):
        self.adapter.register_uri(
            'GET', 'http://image.example.com/v2/images',
            json=dict(images=[]))
        self.assertRaises(exc.OpenStackCloudResourceNotFound,
                          self.cloud.download_image, 'fake_image',
                          output_path='fake_path')

    def _register_image_mocks(self):
        self.adapter.register_uri(
            'GET', 'http://image.example.com/v2/images',
            json=self.fake_search_return)
        self.adapter.register_uri(
            'GET', 'http://image.example.com/v2/images/{id}/file'.format(
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

    def test_download_image_with_path(self):
        self._register_image_mocks()
        output_file = tempfile.NamedTemporaryFile()
        self.cloud.download_image('fake_image', output_path=output_file.name)
        output_file.seek(0)
        self.assertEqual(output_file.read(), self.output)

    def test_empty_list_images(self):
        self.adapter.register_uri(
            'GET', 'http://image.example.com/v2/images', json={'images': []})
        self.assertEqual([], self.cloud.list_images())

    def test_list_images(self):
        self.adapter.register_uri(
            'GET', 'http://image.example.com/v2/images',
            json=self.fake_search_return)
        self.assertEqual(
            self.cloud._normalize_images([self.fake_image_dict]),
            self.cloud.list_images())

    def test_create_image_put_v2(self):
        self.cloud.image_api_use_tasks = False

        self.adapter.register_uri(
            'GET', 'http://image.example.com/v2/images', [
                dict(json={'images': []}),
                dict(json=self.fake_search_return),
            ])
        self.adapter.register_uri(
            'POST', 'http://image.example.com/v2/images',
            json=self.fake_image_dict,
        )
        self.adapter.register_uri(
            'PUT', 'http://image.example.com/v2/images/{id}/file'.format(
                id=self.image_id),
            request_headers={'Content-Type': 'application/octet-stream'})

        self.cloud.create_image(
            'fake_image', self.imagefile.name, wait=True, timeout=1,
            is_public=False)

        calls = [
            dict(method='GET', url='http://192.168.0.19:35357/'),
            dict(method='POST', url='http://example.com/v2.0/tokens'),
            dict(method='GET', url='http://image.example.com/'),
            dict(method='GET', url='http://image.example.com/v2/images'),
            dict(method='POST', url='http://image.example.com/v2/images'),
            dict(
                method='PUT',
                url='http://image.example.com/v2/images/{id}/file'.format(
                    id=self.image_id)),
            dict(method='GET', url='http://image.example.com/v2/images'),
        ]
        for x in range(0, len(calls)):
            self.assertEqual(
                calls[x]['method'], self.adapter.request_history[x].method)
            self.assertEqual(
                calls[x]['url'], self.adapter.request_history[x].url)
        self.assertEqual(
            self.adapter.request_history[4].json(), {
                u'container_format': u'bare',
                u'disk_format': u'qcow2',
                u'name': u'fake_image',
                u'owner_specified.shade.md5': NO_MD5,
                u'owner_specified.shade.object': u'images/fake_image',
                u'owner_specified.shade.sha256': NO_SHA256,
                u'visibility': u'private'
            })
        self.assertEqual(self.adapter.request_history[5].text.read(), b'\x00')


class TestMockImage(base.TestCase):

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

    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, '_get_file_hashes')
    @mock.patch.object(shade.OpenStackCloud, '_image_client')
    @mock.patch.object(shade.OpenStackCloud, 'swift_client')
    @mock.patch.object(shade.OpenStackCloud, 'swift_service')
    def test_create_image_task(self,
                               swift_service_mock,
                               swift_mock,
                               mock_image_client,
                               get_file_hashes,
                               mock_api_version):
        mock_api_version.return_value = '2'
        self.cloud.image_api_use_tasks = True

        class Container(object):
            name = 'image_upload_v2_test_container'

        fake_container = Container()
        swift_mock.get_capabilities.return_value = {
            'swift': {
                'max_file_size': 1000
            }
        }
        swift_mock.put_container.return_value = fake_container
        swift_mock.head_object.return_value = {}

        fake_md5 = "fake-md5"
        fake_sha256 = "fake-sha256"
        get_file_hashes.return_value = (fake_md5, fake_sha256)

        fake_image = munch.Munch(
            id='a35e8afc-cae9-4e38-8441-2cd465f79f7b', name='name-99',
            status='active', visibility='private')

        args = munch.Munch(
            id='21FBD9A7-85EC-4E07-9D58-72F1ACF7CB1F',
            status='success',
            type='import',
            result={
                'image_id': 'a35e8afc-cae9-4e38-8441-2cd465f79f7b',
            },
        )

        # TODO(mordred): When we move this to requests_mock, we need to
        # add a test that throwing a 503 response causes a retry
        mock_image_client.get.side_effect = [
            [],
            [],
            args,
            [fake_image],
            [fake_image],
            [fake_image],
        ]
        self._call_create_image(name='name-99',
                                container='image_upload_v2_test_container')
        args = {'header': ['x-object-meta-x-shade-md5:fake-md5',
                           'x-object-meta-x-shade-sha256:fake-sha256'],
                'segment_size': 1000,
                'use_slo': True}
        swift_service_mock.upload.assert_called_with(
            container='image_upload_v2_test_container',
            objects=mock.ANY,
            options=args)

        mock_image_client.post.assert_called_with(
            '/tasks',
            data=dict(
                type='import', input={
                    'import_from': 'image_upload_v2_test_container/name-99',
                    'image_properties': {'name': 'name-99'}}))
        object_path = 'image_upload_v2_test_container/name-99'
        args = {'owner_specified.shade.md5': fake_md5,
                'owner_specified.shade.sha256': fake_sha256,
                'owner_specified.shade.object': object_path,
                'image_id': 'a35e8afc-cae9-4e38-8441-2cd465f79f7b'}
        mock_image_client.patch.assert_called_with(
            '/images/a35e8afc-cae9-4e38-8441-2cd465f79f7b',
            json=sorted([
                {
                    u'op': u'add',
                    u'value': 'image_upload_v2_test_container/name-99',
                    u'path': u'/owner_specified.shade.object'
                }, {
                    u'op': u'add',
                    u'value': 'fake-md5',
                    u'path': u'/owner_specified.shade.md5'
                }, {
                    u'op': u'add', u'value': 'fake-sha256',
                    u'path': u'/owner_specified.shade.sha256'
                }], key=operator.itemgetter('value')),
            headers={
                'Content-Type': 'application/openstack-images-v2.1-json-patch'
            })

        self.assertEqual(
            self._munch_images(fake_image), self.cloud.list_images())
