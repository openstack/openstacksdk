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

import tempfile
import uuid

import mock
import six

import shade
from shade import exc
from shade.tests.unit import base


class TestImage(base.TestCase):

    def setUp(self):
        super(TestImage, self).setUp()
        self.image_id = str(uuid.uuid4())
        self.fake_search_return = [{
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
            u'protected': False}]
        self.output = six.BytesIO()
        self.output.write(uuid.uuid4().bytes)
        self.output.seek(0)

    def test_download_image_no_output(self):
        self.assertRaises(exc.OpenStackCloudException,
                          self.cloud.download_image, 'fake_image')

    def test_download_image_two_outputs(self):
        fake_fd = six.BytesIO()
        self.assertRaises(exc.OpenStackCloudException,
                          self.cloud.download_image, 'fake_image',
                          output_path='fake_path', output_file=fake_fd)

    @mock.patch.object(shade.OpenStackCloud, 'search_images', return_value=[])
    def test_download_image_no_images_found(self, mock_search):
        self.assertRaises(exc.OpenStackCloudResourceNotFound,
                          self.cloud.download_image, 'fake_image',
                          output_path='fake_path')

    @mock.patch.object(shade.OpenStackCloud, 'glance_client')
    @mock.patch.object(shade.OpenStackCloud, 'search_images')
    def test_download_image_with_fd(self, mock_search, mock_glance):
        output_file = six.BytesIO()
        mock_glance.images.data.return_value = self.output
        mock_search.return_value = self.fake_search_return
        self.cloud.download_image('fake_image', output_file=output_file)
        mock_glance.images.data.assert_called_once_with(self.image_id)
        output_file.seek(0)
        self.output.seek(0)
        self.assertEqual(output_file.read(), self.output.read())

    @mock.patch.object(shade.OpenStackCloud, 'glance_client')
    @mock.patch.object(shade.OpenStackCloud, 'search_images')
    def test_download_image_with_path(self, mock_search, mock_glance):
        output_file = tempfile.NamedTemporaryFile()
        mock_glance.images.data.return_value = self.output
        mock_search.return_value = self.fake_search_return
        self.cloud.download_image('fake_image',
                                  output_path=output_file.name)
        mock_glance.images.data.assert_called_once_with(self.image_id)
        output_file.seek(0)
        self.output.seek(0)
        self.assertEqual(output_file.read(), self.output.read())
