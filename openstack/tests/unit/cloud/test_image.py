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

import io
import operator
import tempfile
from unittest import mock
import uuid

from openstack.cloud import meta
from openstack import exceptions
from openstack.image.v1 import image as image_v1
from openstack.image.v2 import image
from openstack.tests import fakes
from openstack.tests.unit import base


IMPORT_METHODS = 'glance-direct,web-download'


class BaseTestImage(base.TestCase):
    def setUp(self):
        super().setUp()
        self.image_id = str(uuid.uuid4())
        self.image_name = self.getUniqueString('image')
        self.object_name = f'images/{self.image_name}'
        self.imagefile = tempfile.NamedTemporaryFile(delete=False)
        data = b'\2\0'
        self.imagefile.write(data)
        self.imagefile.close()
        self.output = data
        self.fake_image_dict = fakes.make_fake_image(
            image_id=self.image_id,
            image_name=self.image_name,
            data=self.imagefile.name,
        )
        self.fake_search_return = {'images': [self.fake_image_dict]}
        self.container_name = self.getUniqueString('container')

    def _compare_images(self, exp, real):
        self.assertDictEqual(
            image.Image(**exp).to_dict(computed=False),
            real.to_dict(computed=False),
        )

    def _compare_images_v1(self, exp, real):
        self.assertDictEqual(
            image_v1.Image(**exp).to_dict(computed=False),
            real.to_dict(computed=False),
        )


class TestImage(BaseTestImage):
    def setUp(self):
        super().setUp()
        self.use_glance()

    def test_download_image_no_output(self):
        self.assertRaises(
            exceptions.SDKException,
            self.cloud.download_image,
            self.image_name,
        )

    def test_download_image_two_outputs(self):
        fake_fd = io.BytesIO()
        self.assertRaises(
            exceptions.SDKException,
            self.cloud.download_image,
            self.image_name,
            output_path='fake_path',
            output_file=fake_fd,
        )

    def test_download_image_no_images_found(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=f'https://image.example.com/v2/images/{self.image_name}',
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=f'https://image.example.com/v2/images?name={self.image_name}',  # noqa: E501
                    json=dict(images=[]),
                ),
                dict(
                    method='GET',
                    uri='https://image.example.com/v2/images?os_hidden=True',
                    json=dict(images=[]),
                ),
            ]
        )
        self.assertRaises(
            exceptions.NotFoundException,
            self.cloud.download_image,
            self.image_name,
            output_path='fake_path',
        )
        self.assert_calls()

    def _register_image_mocks(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=f'https://image.example.com/v2/images/{self.image_name}',
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=f'https://image.example.com/v2/images?name={self.image_name}',  # noqa: E501
                    json=self.fake_search_return,
                ),
                dict(
                    method='GET',
                    uri=f'https://image.example.com/v2/images/{self.image_id}/file',
                    content=self.output,
                    headers={
                        'Content-Type': 'application/octet-stream',
                        'Content-MD5': self.fake_image_dict['checksum'],
                    },
                ),
            ]
        )

    def test_download_image_with_fd(self):
        self._register_image_mocks()
        output_file = io.BytesIO()
        self.cloud.download_image(self.image_name, output_file=output_file)
        output_file.seek(0)
        self.assertEqual(output_file.read(), self.output)
        self.assert_calls()

    def test_download_image_with_path(self):
        self._register_image_mocks()
        output_file = tempfile.NamedTemporaryFile()
        self.cloud.download_image(
            self.image_name, output_path=output_file.name
        )
        output_file.seek(0)
        self.assertEqual(output_file.read(), self.output)
        self.assert_calls()

    @mock.patch('openstack.image.v2._proxy.Proxy.find_image')
    def test_get_images(self, mock_find):
        image1 = dict(id='123', name='mickey')
        mock_find.return_value = image1
        r = self.cloud.get_image('mickey')
        self.assertIsNotNone(r)
        self.assertDictEqual(image1, r)

    @mock.patch('openstack.image.v2._proxy.Proxy.find_image')
    def test_get_image_not_found(self, mock_find):
        mock_find.return_value = None
        r = self.cloud.get_image('doesNotExist')
        self.assertIsNone(r)

    def test_get_image_name(self, cloud=None):
        cloud = cloud or self.cloud
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image', append=['images'], base_url_append='v2'
                    ),
                    json=self.fake_search_return,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image', append=['images'], base_url_append='v2'
                    ),
                    json=self.fake_search_return,
                ),
            ]
        )

        self.assertEqual(self.image_name, cloud.get_image_name(self.image_id))
        self.assertEqual(
            self.image_name, cloud.get_image_name(self.image_name)
        )

        self.assert_calls()

    def test_get_image_by_id(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images', self.image_id],
                        base_url_append='v2',
                    ),
                    json=self.fake_image_dict,
                )
            ]
        )
        self._compare_images(
            self.fake_image_dict, self.cloud.get_image_by_id(self.image_id)
        )
        self.assert_calls()

    def test_get_image_id(self, cloud=None):
        cloud = cloud or self.cloud
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image', append=['images'], base_url_append='v2'
                    ),
                    json=self.fake_search_return,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image', append=['images'], base_url_append='v2'
                    ),
                    json=self.fake_search_return,
                ),
            ]
        )

        self.assertEqual(self.image_id, cloud.get_image_id(self.image_id))
        self.assertEqual(self.image_id, cloud.get_image_id(self.image_name))

        self.assert_calls()

    def test_get_image_name_operator(self):
        # This should work the same as non-operator, just verifying it does.
        self.test_get_image_name(cloud=self.cloud)

    def test_get_image_id_operator(self):
        # This should work the same as the other test, just verifying it does.
        self.test_get_image_id(cloud=self.cloud)

    def test_empty_list_images(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image', append=['images'], base_url_append='v2'
                    ),
                    json={'images': []},
                )
            ]
        )
        self.assertEqual([], self.cloud.list_images())
        self.assert_calls()

    def test_list_images(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image', append=['images'], base_url_append='v2'
                    ),
                    json=self.fake_search_return,
                )
            ]
        )
        [
            self._compare_images(a, b)
            for a, b in zip([self.fake_image_dict], self.cloud.list_images())
        ]
        self.assert_calls()

    def test_list_images_show_all(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images'],
                        base_url_append='v2',
                        qs_elements=['member_status=all'],
                    ),
                    json=self.fake_search_return,
                )
            ]
        )
        [
            self._compare_images(a, b)
            for a, b in zip(
                [self.fake_image_dict], self.cloud.list_images(show_all=True)
            )
        ]
        self.assert_calls()

    def test_list_images_show_all_deleted(self):
        deleted_image = self.fake_image_dict.copy()
        deleted_image['status'] = 'deleted'
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images'],
                        base_url_append='v2',
                        qs_elements=['member_status=all'],
                    ),
                    json={'images': [self.fake_image_dict, deleted_image]},
                )
            ]
        )
        [
            self._compare_images(a, b)
            for a, b in zip(
                [self.fake_image_dict], self.cloud.list_images(show_all=True)
            )
        ]
        self.assert_calls()

    def test_list_images_no_filter_deleted(self):
        deleted_image = self.fake_image_dict.copy()
        deleted_image['status'] = 'deleted'
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image', append=['images'], base_url_append='v2'
                    ),
                    json={'images': [self.fake_image_dict, deleted_image]},
                )
            ]
        )
        [
            self._compare_images(a, b)
            for a, b in zip(
                [self.fake_image_dict],
                self.cloud.list_images(filter_deleted=False),
            )
        ]
        self.assert_calls()

    def test_list_images_filter_deleted(self):
        deleted_image = self.fake_image_dict.copy()
        deleted_image['status'] = 'deleted'
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image', append=['images'], base_url_append='v2'
                    ),
                    json={'images': [self.fake_image_dict, deleted_image]},
                )
            ]
        )
        [
            self._compare_images(a, b)
            for a, b in zip([self.fake_image_dict], self.cloud.list_images())
        ]
        self.assert_calls()

    def test_list_images_string_properties(self):
        image_dict = self.fake_image_dict.copy()
        image_dict['properties'] = 'list,of,properties'
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image', append=['images'], base_url_append='v2'
                    ),
                    json={'images': [image_dict]},
                ),
            ]
        )
        images = self.cloud.list_images()
        [self._compare_images(a, b) for a, b in zip([image_dict], images)]

        self.assertEqual(
            images[0]['properties']['properties'], 'list,of,properties'
        )
        self.assert_calls()

    def test_list_images_paginated(self):
        marker = str(uuid.uuid4())
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image', append=['images'], base_url_append='v2'
                    ),
                    json={
                        'images': [self.fake_image_dict],
                        'next': f'/v2/images?marker={marker}',
                    },
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images'],
                        base_url_append='v2',
                        qs_elements=[f'marker={marker}'],
                    ),
                    json=self.fake_search_return,
                ),
            ]
        )
        [
            self._compare_images(a, b)
            for a, b in zip([self.fake_image_dict], self.cloud.list_images())
        ]
        self.assert_calls()

    def test_create_image_put_v2_no_import(self):
        self.cloud.image_api_use_tasks = False

        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images', self.image_name],
                        base_url_append='v2',
                    ),
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images'],
                        base_url_append='v2',
                        qs_elements=['name=' + self.image_name],
                    ),
                    validate=dict(),
                    json={'images': []},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images'],
                        base_url_append='v2',
                        qs_elements=['os_hidden=True'],
                    ),
                    json={'images': []},
                ),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'image', append=['images'], base_url_append='v2'
                    ),
                    json=self.fake_image_dict,
                    validate=dict(
                        json={
                            'container_format': 'bare',
                            'disk_format': 'qcow2',
                            'name': self.image_name,
                            'owner_specified.openstack.md5': self.fake_image_dict[  # noqa: E501
                                'owner_specified.openstack.md5'
                            ],
                            'owner_specified.openstack.object': self.object_name,  # noqa: E501
                            'owner_specified.openstack.sha256': self.fake_image_dict[  # noqa: E501
                                'owner_specified.openstack.sha256'
                            ],
                            'visibility': 'private',
                            'tags': ['tag1', 'tag2'],
                        }
                    ),
                ),
                dict(
                    method='PUT',
                    uri=self.get_mock_url(
                        'image',
                        append=['images', self.image_id, 'file'],
                        base_url_append='v2',
                    ),
                    request_headers={
                        'Content-Type': 'application/octet-stream'
                    },
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images', self.fake_image_dict['id']],
                        base_url_append='v2',
                    ),
                    json=self.fake_image_dict,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images', self.fake_image_dict['id']],
                        base_url_append='v2',
                    ),
                    complete_qs=True,
                    json=self.fake_image_dict,
                ),
            ]
        )

        self.cloud.create_image(
            self.image_name,
            self.imagefile.name,
            wait=True,
            timeout=1,
            tags=['tag1', 'tag2'],
            is_public=False,
            validate_checksum=True,
        )

        self.assert_calls()
        self.assertEqual(
            self.adapter.request_history[7].text.read(), self.output
        )

    def test_create_image_put_v2_import_supported(self):
        self.cloud.image_api_use_tasks = False

        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images', self.image_name],
                        base_url_append='v2',
                    ),
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images'],
                        base_url_append='v2',
                        qs_elements=['name=' + self.image_name],
                    ),
                    validate=dict(),
                    json={'images': []},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images'],
                        base_url_append='v2',
                        qs_elements=['os_hidden=True'],
                    ),
                    json={'images': []},
                ),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'image', append=['images'], base_url_append='v2'
                    ),
                    json=self.fake_image_dict,
                    headers={
                        'OpenStack-image-import-methods': IMPORT_METHODS,
                    },
                    validate=dict(
                        json={
                            'container_format': 'bare',
                            'disk_format': 'qcow2',
                            'name': self.image_name,
                            'owner_specified.openstack.md5': self.fake_image_dict[  # noqa: E501
                                'owner_specified.openstack.md5'
                            ],
                            'owner_specified.openstack.object': self.object_name,  # noqa: E501
                            'owner_specified.openstack.sha256': self.fake_image_dict[  # noqa: E501
                                'owner_specified.openstack.sha256'
                            ],
                            'visibility': 'private',
                            'tags': ['tag1', 'tag2'],
                        }
                    ),
                ),
                dict(
                    method='PUT',
                    uri=self.get_mock_url(
                        'image',
                        append=['images', self.image_id, 'file'],
                        base_url_append='v2',
                    ),
                    request_headers={
                        'Content-Type': 'application/octet-stream'
                    },
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images', self.fake_image_dict['id']],
                        base_url_append='v2',
                    ),
                    json=self.fake_image_dict,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images', self.fake_image_dict['id']],
                        base_url_append='v2',
                    ),
                    complete_qs=True,
                    json=self.fake_image_dict,
                ),
            ]
        )

        self.cloud.create_image(
            self.image_name,
            self.imagefile.name,
            wait=True,
            timeout=1,
            tags=['tag1', 'tag2'],
            is_public=False,
            validate_checksum=True,
        )

        self.assert_calls()
        self.assertEqual(
            self.adapter.request_history[7].text.read(), self.output
        )

    def test_create_image_use_import(self):
        self.cloud.image_api_use_tasks = False

        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images', self.image_name],
                        base_url_append='v2',
                    ),
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images'],
                        base_url_append='v2',
                        qs_elements=['name=' + self.image_name],
                    ),
                    validate=dict(),
                    json={'images': []},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images'],
                        base_url_append='v2',
                        qs_elements=['os_hidden=True'],
                    ),
                    json={'images': []},
                ),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'image', append=['images'], base_url_append='v2'
                    ),
                    json=self.fake_image_dict,
                    headers={
                        'OpenStack-image-import-methods': IMPORT_METHODS,
                    },
                    validate=dict(
                        json={
                            'container_format': 'bare',
                            'disk_format': 'qcow2',
                            'name': self.image_name,
                            'owner_specified.openstack.md5': self.fake_image_dict[  # noqa: E501
                                'owner_specified.openstack.md5'
                            ],
                            'owner_specified.openstack.object': self.object_name,  # noqa: E501
                            'owner_specified.openstack.sha256': self.fake_image_dict[  # noqa: E501
                                'owner_specified.openstack.sha256'
                            ],
                            'visibility': 'private',
                            'tags': ['tag1', 'tag2'],
                        }
                    ),
                ),
                dict(
                    method='PUT',
                    uri=self.get_mock_url(
                        'image',
                        append=['images', self.image_id, 'stage'],
                        base_url_append='v2',
                    ),
                    request_headers={
                        'Content-Type': 'application/octet-stream'
                    },
                ),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'image',
                        append=['images', self.image_id, 'import'],
                        base_url_append='v2',
                    ),
                    json={'method': {'name': 'glance-direct'}},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images', self.fake_image_dict['id']],
                        base_url_append='v2',
                    ),
                    json=self.fake_image_dict,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images', self.fake_image_dict['id']],
                        base_url_append='v2',
                    ),
                    complete_qs=True,
                    json=self.fake_image_dict,
                ),
            ]
        )

        self.cloud.create_image(
            self.image_name,
            self.imagefile.name,
            wait=True,
            timeout=1,
            tags=['tag1', 'tag2'],
            is_public=False,
            validate_checksum=True,
            use_import=True,
        )

        self.assert_calls()
        self.assertEqual(
            self.adapter.request_history[7].text.read(), self.output
        )

    def test_create_image_task(self):
        self.cloud.image_api_use_tasks = True
        endpoint = self.cloud.object_store.get_endpoint()

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
        del image_no_checksums['owner_specified.openstack.md5']
        del image_no_checksums['owner_specified.openstack.sha256']
        del image_no_checksums['owner_specified.openstack.object']

        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images', self.image_name],
                        base_url_append='v2',
                    ),
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images'],
                        base_url_append='v2',
                        qs_elements=['name=' + self.image_name],
                    ),
                    validate=dict(),
                    json={'images': []},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images'],
                        base_url_append='v2',
                        qs_elements=['os_hidden=True'],
                    ),
                    json={'images': []},
                ),
                dict(
                    method='HEAD',
                    uri=f'{endpoint}/{self.container_name}',
                    status_code=404,
                ),
                dict(
                    method='PUT',
                    uri=f'{endpoint}/{self.container_name}',
                    status_code=201,
                    headers={
                        'Date': 'Fri, 16 Dec 2016 18:21:20 GMT',
                        'Content-Length': '0',
                        'Content-Type': 'text/html; charset=UTF-8',
                    },
                ),
                dict(
                    method='HEAD',
                    uri=f'{endpoint}/{self.container_name}',
                    headers={
                        'Content-Length': '0',
                        'X-Container-Object-Count': '0',
                        'Accept-Ranges': 'bytes',
                        'X-Storage-Policy': 'Policy-0',
                        'Date': 'Fri, 16 Dec 2016 18:29:05 GMT',
                        'X-Timestamp': '1481912480.41664',
                        'X-Trans-Id': 'tx60ec128d9dbf44b9add68-0058543271dfw1',
                        'X-Container-Bytes-Used': '0',
                        'Content-Type': 'text/plain; charset=utf-8',
                    },
                ),
                dict(
                    method='GET',
                    # This is explicitly not using get_mock_url because that
                    # gets us a project-id oriented URL.
                    uri='https://object-store.example.com/info',
                    json=dict(
                        swift={'max_file_size': 1000},
                        slo={'min_segment_size': 500},
                    ),
                ),
                dict(
                    method='HEAD',
                    uri=f'{endpoint}/{self.container_name}/{self.image_name}',
                    status_code=404,
                ),
                dict(
                    method='PUT',
                    uri=f'{endpoint}/{self.container_name}/{self.image_name}',
                    status_code=201,
                    validate=dict(
                        headers={
                            'X-Object-Meta-x-sdk-md5': self.fake_image_dict[
                                'owner_specified.openstack.md5'
                            ],
                            'X-Object-Meta-x-sdk-sha256': self.fake_image_dict[
                                'owner_specified.openstack.sha256'
                            ],
                        }
                    ),
                ),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'image', append=['tasks'], base_url_append='v2'
                    ),
                    json={'id': task_id, 'status': 'processing'},
                    validate=dict(
                        json=dict(
                            type='import',
                            input={
                                'import_from': f'{self.container_name}/{self.image_name}',
                                'image_properties': {'name': self.image_name},
                            },
                        )
                    ),
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['tasks', task_id],
                        base_url_append='v2',
                    ),
                    status_code=503,
                    text='Random error',
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['tasks', task_id],
                        base_url_append='v2',
                    ),
                    json=args,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images', self.image_id],
                        base_url_append='v2',
                    ),
                    json=image_no_checksums,
                ),
                dict(
                    method='PATCH',
                    uri=self.get_mock_url(
                        'image',
                        append=['images', self.image_id],
                        base_url_append='v2',
                    ),
                    validate=dict(
                        json=sorted(
                            [
                                {
                                    'op': 'add',
                                    'value': f'{self.container_name}/{self.image_name}',
                                    'path': '/owner_specified.openstack.object',  # noqa: E501
                                },
                                {
                                    'op': 'add',
                                    'value': self.fake_image_dict[
                                        'owner_specified.openstack.md5'
                                    ],
                                    'path': '/owner_specified.openstack.md5',
                                },
                                {
                                    'op': 'add',
                                    'value': self.fake_image_dict[
                                        'owner_specified.openstack.sha256'
                                    ],
                                    'path': '/owner_specified.openstack.sha256',  # noqa: E501
                                },
                            ],
                            key=operator.itemgetter('path'),
                        ),
                        headers={
                            'Content-Type': 'application/openstack-images-v2.1-json-patch'  # noqa: E501
                        },
                    ),
                    json=self.fake_search_return,
                ),
                dict(
                    method='HEAD',
                    uri=f'{endpoint}/{self.container_name}/{self.image_name}',
                    headers={
                        'X-Timestamp': '1429036140.50253',
                        'X-Trans-Id': 'txbbb825960a3243b49a36f-005a0dadaedfw1',
                        'Content-Length': '1290170880',
                        'Last-Modified': 'Tue, 14 Apr 2015 18:29:01 GMT',
                        'X-Object-Meta-X-Sdk-Sha256': self.fake_image_dict[
                            'owner_specified.openstack.sha256'
                        ],
                        'X-Object-Meta-X-Sdk-Md5': self.fake_image_dict[
                            'owner_specified.openstack.md5'
                        ],
                        'Date': 'Thu, 16 Nov 2017 15:24:30 GMT',
                        'Accept-Ranges': 'bytes',
                        'Content-Type': 'application/octet-stream',
                        'Etag': fakes.NO_MD5,
                    },
                ),
                dict(
                    method='DELETE',
                    uri=f'{endpoint}/{self.container_name}/{self.image_name}',
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images', self.image_id],
                        base_url_append='v2',
                    ),
                    complete_qs=True,
                    json=image_no_checksums,
                ),
            ]
        )

        self.cloud.create_image(
            self.image_name,
            self.imagefile.name,
            wait=True,
            timeout=1,
            disk_format='vhd',
            container_format='ovf',
            is_public=False,
            validate_checksum=True,
            container=self.container_name,
        )

        self.assert_calls()

    def test_delete_autocreated_no_tasks(self):
        self.use_keystone_v3()
        self.cloud.image_api_use_tasks = False
        deleted = self.cloud.delete_autocreated_image_objects(
            container=self.container_name
        )
        self.assertFalse(deleted)
        self.assert_calls([])

    def test_delete_image_task(self):
        self.cloud.image_api_use_tasks = True
        endpoint = self.cloud.object_store.get_endpoint()

        object_path = self.fake_image_dict['owner_specified.openstack.object']

        image_no_checksums = self.fake_image_dict.copy()
        del image_no_checksums['owner_specified.openstack.md5']
        del image_no_checksums['owner_specified.openstack.sha256']
        del image_no_checksums['owner_specified.openstack.object']

        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images', self.image_id],
                        base_url_append='v2',
                    ),
                    json=self.fake_image_dict,
                ),
                dict(
                    method='DELETE',
                    uri=f'https://image.example.com/v2/images/{self.image_id}',
                ),
                dict(
                    method='HEAD',
                    uri=f'{endpoint}/{object_path}',
                    headers={
                        'X-Timestamp': '1429036140.50253',
                        'X-Trans-Id': 'txbbb825960a3243b49a36f-005a0dadaedfw1',
                        'Content-Length': '1290170880',
                        'Last-Modified': 'Tue, 14 Apr 2015 18:29:01 GMT',
                        'X-Object-Meta-X-Sdk-Sha256': self.fake_image_dict[
                            'owner_specified.openstack.sha256'
                        ],
                        'X-Object-Meta-X-Sdk-Md5': self.fake_image_dict[
                            'owner_specified.openstack.md5'
                        ],
                        'Date': 'Thu, 16 Nov 2017 15:24:30 GMT',
                        'Accept-Ranges': 'bytes',
                        'Content-Type': 'application/octet-stream',
                        'Etag': fakes.NO_MD5,
                    },
                ),
                dict(
                    method='DELETE',
                    uri=f'{endpoint}/{object_path}',
                ),
            ]
        )

        self.cloud.delete_image(self.image_id)

        self.assert_calls()

    def test_delete_autocreated_image_objects(self):
        self.use_keystone_v3()
        self.cloud.image_api_use_tasks = True
        endpoint = self.cloud.object_store.get_endpoint()
        other_image = self.getUniqueString('no-delete')

        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        service_type='object-store',
                        resource=self.container_name,
                        qs_elements=['format=json'],
                    ),
                    json=[
                        {
                            'content_type': 'application/octet-stream',
                            'bytes': 1437258240,
                            'hash': '249219347276c331b87bf1ac2152d9af',
                            'last_modified': '2015-02-16T17:50:05.289600',
                            'name': other_image,
                        },
                        {
                            'content_type': 'application/octet-stream',
                            'bytes': 1290170880,
                            'hash': fakes.NO_MD5,
                            'last_modified': '2015-04-14T18:29:00.502530',
                            'name': self.image_name,
                        },
                    ],
                ),
                dict(
                    method='HEAD',
                    uri=self.get_mock_url(
                        service_type='object-store',
                        resource=self.container_name,
                        append=[other_image],
                    ),
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
                    },
                ),
                dict(
                    method='HEAD',
                    uri=self.get_mock_url(
                        service_type='object-store',
                        resource=self.container_name,
                        append=[self.image_name],
                    ),
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
                        (
                            'X-Object-Meta-'
                            + self.cloud._OBJECT_AUTOCREATE_KEY
                        ): 'true',
                        'Etag': fakes.NO_MD5,
                        'X-Static-Large-Object': 'false',
                    },
                ),
                dict(
                    method='DELETE',
                    uri=f'{endpoint}/{self.container_name}/{self.image_name}',
                ),
            ]
        )

        deleted = self.cloud.delete_autocreated_image_objects(
            container=self.container_name
        )
        self.assertTrue(deleted)

        self.assert_calls()

    def _image_dict(self, fake_image):
        return self.cloud._normalize_image(meta.obj_to_munch(fake_image))

    def _call_create_image(self, name, **kwargs):
        imagefile = tempfile.NamedTemporaryFile(delete=False)
        imagefile.write(b'\0')
        imagefile.close()
        self.cloud.create_image(
            name,
            imagefile.name,
            wait=True,
            timeout=1,
            is_public=False,
            validate_checksum=True,
            **kwargs,
        )

    def test_create_image_put_v1(self):
        self.cloud.config.config['image_api_version'] = '1'

        args = {
            'name': self.image_name,
            'container_format': 'bare',
            'disk_format': 'qcow2',
            'properties': {
                'owner_specified.openstack.md5': fakes.NO_MD5,
                'owner_specified.openstack.sha256': fakes.NO_SHA256,
                'owner_specified.openstack.object': f'images/{self.image_name}',
                'is_public': False,
            },
        }

        ret = args.copy()
        ret['id'] = self.image_id
        ret['status'] = 'success'

        self.register_uris(
            [
                dict(
                    method='GET',
                    uri='https://image.example.com/v1/images/'
                    + self.image_name,
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri='https://image.example.com/v1/images/detail?name='
                    + self.image_name,
                    json={'images': []},
                ),
                dict(
                    method='POST',
                    uri='https://image.example.com/v1/images',
                    json={'image': ret},
                    validate=dict(json=args),
                ),
                dict(
                    method='PUT',
                    uri=f'https://image.example.com/v1/images/{self.image_id}',
                    json=ret,
                    validate=dict(
                        headers={
                            'x-image-meta-checksum': fakes.NO_MD5,
                            'x-glance-registry-purge-props': 'false',
                        }
                    ),
                ),
                dict(
                    method='GET',
                    uri='https://image.example.com/v1/images/detail',
                    json={'images': [ret]},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images', self.image_id],
                        base_url_append='v1',
                    ),
                    complete_qs=True,
                    json=ret,
                ),
            ]
        )
        self._call_create_image(self.image_name)
        [
            self._compare_images_v1(b, a)
            for a, b in zip(self.cloud.list_images(), [ret])
        ]

    def test_create_image_put_v1_bad_delete(self):
        self.cloud.config.config['image_api_version'] = '1'

        args = {
            'name': self.image_name,
            'container_format': 'bare',
            'disk_format': 'qcow2',
            'properties': {
                'owner_specified.openstack.md5': fakes.NO_MD5,
                'owner_specified.openstack.sha256': fakes.NO_SHA256,
                'owner_specified.openstack.object': f'images/{self.image_name}',
                'is_public': False,
            },
            'validate_checksum': True,
        }

        ret = args.copy()
        ret['id'] = self.image_id
        ret['status'] = 'success'

        self.register_uris(
            [
                dict(
                    method='GET',
                    uri='https://image.example.com/v1/images/'
                    + self.image_name,
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri='https://image.example.com/v1/images/detail?name='
                    + self.image_name,
                    json={'images': []},
                ),
                dict(
                    method='POST',
                    uri='https://image.example.com/v1/images',
                    json={'image': ret},
                    validate=dict(json=args),
                ),
                dict(
                    method='PUT',
                    uri=f'https://image.example.com/v1/images/{self.image_id}',
                    status_code=400,
                    validate=dict(
                        headers={
                            'x-image-meta-checksum': fakes.NO_MD5,
                            'x-glance-registry-purge-props': 'false',
                        }
                    ),
                ),
                dict(
                    method='DELETE',
                    uri=f'https://image.example.com/v1/images/{self.image_id}',
                    json={'images': [ret]},
                ),
            ]
        )

        self.assertRaises(
            exceptions.HttpException,
            self._call_create_image,
            self.image_name,
        )

        self.assert_calls()

    def test_update_image_no_patch(self):
        self.cloud.image_api_use_tasks = False

        args = {
            'name': self.image_name,
            'container_format': 'bare',
            'disk_format': 'qcow2',
            'owner_specified.openstack.md5': fakes.NO_MD5,
            'owner_specified.openstack.sha256': fakes.NO_SHA256,
            'owner_specified.openstack.object': f'images/{self.image_name}',
            'visibility': 'private',
        }

        ret = args.copy()
        ret['id'] = self.image_id
        ret['status'] = 'success'

        self.cloud.update_image_properties(
            image=image.Image.existing(**ret),
            **{
                'owner_specified.openstack.object': f'images/{self.image_name}'
            },
        )

        self.assert_calls()

    def test_create_image_put_v2_bad_delete(self):
        self.cloud.image_api_use_tasks = False

        args = {
            'name': self.image_name,
            'container_format': 'bare',
            'disk_format': 'qcow2',
            'owner_specified.openstack.md5': fakes.NO_MD5,
            'owner_specified.openstack.sha256': fakes.NO_SHA256,
            'owner_specified.openstack.object': f'images/{self.image_name}',
            'visibility': 'private',
        }

        ret = args.copy()
        ret['id'] = self.image_id
        ret['status'] = 'success'

        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images', self.image_name],
                        base_url_append='v2',
                    ),
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images'],
                        base_url_append='v2',
                        qs_elements=['name=' + self.image_name],
                    ),
                    validate=dict(),
                    json={'images': []},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images'],
                        base_url_append='v2',
                        qs_elements=['os_hidden=True'],
                    ),
                    json={'images': []},
                ),
                dict(
                    method='POST',
                    uri='https://image.example.com/v2/images',
                    json=ret,
                    validate=dict(json=args),
                ),
                dict(
                    method='PUT',
                    uri=f'https://image.example.com/v2/images/{self.image_id}/file',
                    status_code=400,
                    validate=dict(
                        headers={
                            'Content-Type': 'application/octet-stream',
                        },
                    ),
                ),
                dict(
                    method='DELETE',
                    uri=f'https://image.example.com/v2/images/{self.image_id}',
                ),
            ]
        )

        self.assertRaises(
            exceptions.HttpException,
            self._call_create_image,
            self.image_name,
        )

        self.assert_calls()

    def test_create_image_put_v2_wrong_checksum_delete(self):
        self.cloud.image_api_use_tasks = False

        fake_image = self.fake_image_dict

        fake_image['owner_specified.openstack.md5'] = 'a'
        fake_image['owner_specified.openstack.sha256'] = 'b'

        self.register_uris(
            [
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'image', append=['images'], base_url_append='v2'
                    ),
                    json=self.fake_image_dict,
                    validate=dict(
                        json={
                            'container_format': 'bare',
                            'disk_format': 'qcow2',
                            'name': self.image_name,
                            'owner_specified.openstack.md5': fake_image[
                                'owner_specified.openstack.md5'
                            ],
                            'owner_specified.openstack.object': self.object_name,  # noqa: E501
                            'owner_specified.openstack.sha256': fake_image[
                                'owner_specified.openstack.sha256'
                            ],
                            'visibility': 'private',
                        }
                    ),
                ),
                dict(
                    method='PUT',
                    uri=self.get_mock_url(
                        'image',
                        append=['images', self.image_id, 'file'],
                        base_url_append='v2',
                    ),
                    request_headers={
                        'Content-Type': 'application/octet-stream'
                    },
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images', self.fake_image_dict['id']],
                        base_url_append='v2',
                    ),
                    json=fake_image,
                ),
                dict(
                    method='DELETE',
                    uri=f'https://image.example.com/v2/images/{self.image_id}',
                ),
            ]
        )

        self.assertRaises(
            exceptions.SDKException,
            self.cloud.create_image,
            self.image_name,
            self.imagefile.name,
            is_public=False,
            md5='a',
            sha256='b',
            allow_duplicates=True,
            validate_checksum=True,
        )

        self.assert_calls()

    def test_create_image_put_bad_int(self):
        self.cloud.image_api_use_tasks = False

        self.assertRaises(
            exceptions.SDKException,
            self._call_create_image,
            self.image_name,
            allow_duplicates=True,
            min_disk='fish',
            min_ram=0,
        )

        self.assert_calls()

    def test_create_image_put_user_int(self):
        self.cloud.image_api_use_tasks = False

        args = {
            'name': self.image_name,
            'container_format': 'bare',
            'disk_format': 'qcow2',
            'owner_specified.openstack.md5': fakes.NO_MD5,
            'owner_specified.openstack.sha256': fakes.NO_SHA256,
            'owner_specified.openstack.object': f'images/{self.image_name}',
            'int_v': '12345',
            'visibility': 'private',
            'min_disk': 0,
            'min_ram': 0,
        }

        ret = args.copy()
        ret['id'] = self.image_id
        ret['status'] = 'success'

        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images', self.image_name],
                        base_url_append='v2',
                    ),
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images'],
                        base_url_append='v2',
                        qs_elements=['name=' + self.image_name],
                    ),
                    validate=dict(),
                    json={'images': []},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images'],
                        base_url_append='v2',
                        qs_elements=['os_hidden=True'],
                    ),
                    json={'images': []},
                ),
                dict(
                    method='POST',
                    uri='https://image.example.com/v2/images',
                    json=ret,
                    validate=dict(json=args),
                ),
                dict(
                    method='PUT',
                    uri=f'https://image.example.com/v2/images/{self.image_id}/file',
                    validate=dict(
                        headers={
                            'Content-Type': 'application/octet-stream',
                        },
                    ),
                ),
                dict(
                    method='GET',
                    uri=f'https://image.example.com/v2/images/{self.image_id}',
                    json=ret,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images', self.image_id],
                        base_url_append='v2',
                    ),
                    complete_qs=True,
                    json=ret,
                ),
            ]
        )

        self._call_create_image(
            self.image_name, min_disk='0', min_ram=0, int_v=12345
        )

        self.assert_calls()

    def test_create_image_put_meta_int(self):
        self.cloud.image_api_use_tasks = False

        args = {
            'name': self.image_name,
            'container_format': 'bare',
            'disk_format': 'qcow2',
            'owner_specified.openstack.md5': fakes.NO_MD5,
            'owner_specified.openstack.sha256': fakes.NO_SHA256,
            'owner_specified.openstack.object': f'images/{self.image_name}',
            'int_v': 12345,
            'visibility': 'private',
            'min_disk': 0,
            'min_ram': 0,
        }

        ret = args.copy()
        ret['id'] = self.image_id
        ret['status'] = 'success'
        ret['checksum'] = fakes.NO_MD5

        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images', self.image_name],
                        base_url_append='v2',
                    ),
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images'],
                        base_url_append='v2',
                        qs_elements=['name=' + self.image_name],
                    ),
                    validate=dict(),
                    json={'images': []},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images'],
                        base_url_append='v2',
                        qs_elements=['os_hidden=True'],
                    ),
                    json={'images': []},
                ),
                dict(
                    method='POST',
                    uri='https://image.example.com/v2/images',
                    json=ret,
                    validate=dict(json=args),
                ),
                dict(
                    method='PUT',
                    uri=f'https://image.example.com/v2/images/{self.image_id}/file',
                    validate=dict(
                        headers={
                            'Content-Type': 'application/octet-stream',
                        },
                    ),
                ),
                dict(
                    method='GET',
                    uri=f'https://image.example.com/v2/images/{self.image_id}',
                    json=ret,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images', self.image_id],
                        base_url_append='v2',
                    ),
                    complete_qs=True,
                    json=ret,
                ),
            ]
        )

        self._call_create_image(
            self.image_name, min_disk='0', min_ram=0, meta={'int_v': 12345}
        )

        self.assert_calls()

    def test_create_image_put_protected(self):
        self.cloud.image_api_use_tasks = False

        args = {
            'name': self.image_name,
            'container_format': 'bare',
            'disk_format': 'qcow2',
            'owner_specified.openstack.md5': fakes.NO_MD5,
            'owner_specified.openstack.sha256': fakes.NO_SHA256,
            'owner_specified.openstack.object': f'images/{self.image_name}',
            'int_v': '12345',
            'protected': False,
            'visibility': 'private',
            'min_disk': 0,
            'min_ram': 0,
        }

        ret = args.copy()
        ret['id'] = self.image_id
        ret['status'] = 'success'
        ret['checksum'] = fakes.NO_MD5

        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images', self.image_name],
                        base_url_append='v2',
                    ),
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images'],
                        base_url_append='v2',
                        qs_elements=['name=' + self.image_name],
                    ),
                    validate=dict(),
                    json={'images': []},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images'],
                        base_url_append='v2',
                        qs_elements=['os_hidden=True'],
                    ),
                    json={'images': []},
                ),
                dict(
                    method='POST',
                    uri='https://image.example.com/v2/images',
                    json=ret,
                    validate=dict(json=args),
                ),
                dict(
                    method='PUT',
                    uri=f'https://image.example.com/v2/images/{self.image_id}/file',
                    validate=dict(
                        headers={
                            'Content-Type': 'application/octet-stream',
                        },
                    ),
                ),
                dict(
                    method='GET',
                    uri=f'https://image.example.com/v2/images/{self.image_id}',
                    json=ret,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images', self.image_id],
                        base_url_append='v2',
                    ),
                    complete_qs=True,
                    json=ret,
                ),
            ]
        )

        self._call_create_image(
            self.image_name,
            min_disk='0',
            min_ram=0,
            properties={'int_v': 12345},
            is_protected=False,
        )

        self.assert_calls()


class TestImageSuburl(BaseTestImage):
    def setUp(self):
        super().setUp()
        self.os_fixture.use_suburl()
        self.os_fixture.build_tokens()
        self.use_keystone_v3()
        self.use_glance(
            image_version_json='image-version-suburl.json',
            image_discovery_url='https://example.com/image',
        )

    def test_list_images(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image', append=['images'], base_url_append='v2'
                    ),
                    json=self.fake_search_return,
                )
            ]
        )
        [
            self._compare_images(b, a)
            for a, b in zip(self.cloud.list_images(), [self.fake_image_dict])
        ]
        self.assert_calls()

    def test_list_images_paginated(self):
        marker = str(uuid.uuid4())
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image', append=['images'], base_url_append='v2'
                    ),
                    json={
                        'images': [self.fake_image_dict],
                        'next': f'/v2/images?marker={marker}',
                    },
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images'],
                        base_url_append='v2',
                        qs_elements=[f'marker={marker}'],
                    ),
                    json=self.fake_search_return,
                ),
            ]
        )
        [
            self._compare_images(b, a)
            for a, b in zip(
                self.cloud.list_images(),
                [self.fake_image_dict, self.fake_image_dict],
            )
        ]
        self.assert_calls()


class TestImageVolume(BaseTestImage):
    def setUp(self):
        super().setUp()
        self.volume_id = str(uuid.uuid4())

    def test_create_image_volume(self):
        self.register_uris(
            [
                self.get_cinder_discovery_mock_dict(),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'volumev3',
                        append=['volumes', self.volume_id, 'action'],
                    ),
                    json={
                        'os-volume_upload_image': {'image_id': self.image_id}
                    },
                    validate=dict(
                        json={
                            'os-volume_upload_image': {
                                'container_format': 'bare',
                                'disk_format': 'qcow2',
                                'force': False,
                                'image_name': 'fake_image',
                            }
                        }
                    ),
                ),
                # NOTE(notmorgan): Glance discovery happens here, insert the
                # glance discovery mock at this point, DO NOT use the
                # .use_glance() method, that is intended only for use in
                # .setUp
                self.get_glance_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images', self.image_id],
                        base_url_append='v2',
                    ),
                    json=self.fake_image_dict,
                ),
            ]
        )

        self.cloud.create_image(
            'fake_image',
            self.imagefile.name,
            wait=True,
            timeout=1,
            volume={'id': self.volume_id},
        )

        self.assert_calls()

    def test_create_image_volume_duplicate(self):
        self.register_uris(
            [
                self.get_cinder_discovery_mock_dict(),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'volumev3',
                        append=['volumes', self.volume_id, 'action'],
                    ),
                    json={
                        'os-volume_upload_image': {'image_id': self.image_id}
                    },
                    validate=dict(
                        json={
                            'os-volume_upload_image': {
                                'container_format': 'bare',
                                'disk_format': 'qcow2',
                                'force': True,
                                'image_name': 'fake_image',
                            }
                        }
                    ),
                ),
                # NOTE(notmorgan): Glance discovery happens here, insert the
                # glance discovery mock at this point, DO NOT use the
                # .use_glance() method, that is intended only for use in
                # .setUp
                self.get_glance_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'image',
                        append=['images', self.image_id],
                        base_url_append='v2',
                    ),
                    json=self.fake_image_dict,
                ),
            ]
        )

        self.cloud.create_image(
            'fake_image',
            self.imagefile.name,
            wait=True,
            timeout=1,
            volume={'id': self.volume_id},
            allow_duplicates=True,
        )

        self.assert_calls()
