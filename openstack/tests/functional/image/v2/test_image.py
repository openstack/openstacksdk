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

    class ImageOpts:
        def __init__(self):
            self.image_api_version = '2'

    def setUp(self):
        super(TestImage, self).setUp()
        opts = self.ImageOpts()
        self.conn = connection.from_config(
            cloud_name=base.TEST_CLOUD_NAME, options=opts)

        self.img = self.conn.image.upload_image(
            name=TEST_IMAGE_NAME,
            disk_format='raw',
            container_format='bare',
            # TODO(mordred): This is not doing what people think it is doing.
            # This is EPICLY broken. However, rather than fixing it as it is,
            # we need to just replace the image upload code with the stuff
            # from shade. Figuring out mapping the crap-tastic arbitrary
            # extra key-value pairs into Resource is going to be fun.
            properties='{"description": "This is not an image"}',
            data=open('CONTRIBUTING.rst', 'r')
        )
        self.addCleanup(self.conn.image.delete_image, self.img)

    def test_get_image(self):
        img2 = self.conn.image.get_image(self.img)
        self.assertEqual(self.img, img2)

    def test_get_images_schema(self):
        schema = self.conn.image.get_images_schema()
        self.assertIsNotNone(schema)

    def test_get_image_schema(self):
        schema = self.conn.image.get_image_schema()
        self.assertIsNotNone(schema)

    def test_get_members_schema(self):
        schema = self.conn.image.get_members_schema()
        self.assertIsNotNone(schema)

    def test_get_member_schema(self):
        schema = self.conn.image.get_member_schema()
        self.assertIsNotNone(schema)

    def test_list_tasks(self):
        tasks = self.conn.image.tasks()
        self.assertIsNotNone(tasks)
