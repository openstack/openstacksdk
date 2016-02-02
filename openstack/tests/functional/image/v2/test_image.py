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

from openstack import connection
from openstack.tests.functional import base

TEST_IMAGE_NAME = 'Test Image'


class TestImage(base.BaseFunctionalTest):

    class ImageOpts(object):
        def __init__(self):
            self.image_api_version = '2'

    @classmethod
    def setUpClass(cls):
        opts = cls.ImageOpts()
        cls.conn = connection.from_config(cloud_name=base.TEST_CLOUD,
                                          options=opts)

        cls.img = cls.conn.image.upload_image(
            name=TEST_IMAGE_NAME,
            disk_format='raw',
            container_format='bare',
            properties='{"description": "This is not an image"}',
            data=open('CONTRIBUTING.rst', 'r')
        )

    @classmethod
    def tearDownClass(cls):
        cls.conn.image.delete_image(cls.img)

    def test_get_image(self):
        img2 = self.conn.image.get_image(self.img)
        self.assertEqual(self.img, img2)
