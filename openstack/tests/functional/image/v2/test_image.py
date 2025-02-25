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

from openstack.image.v2 import image as _image
from openstack.tests.functional.image.v2 import base

# NOTE(stephenfin): This is referenced in the Compute functional tests to avoid
# attempts to boot from it.
TEST_IMAGE_NAME = 'Test Image'


class TestImage(base.BaseImageTest):
    def setUp(self):
        super().setUp()

        # there's a limit on name length
        self.image = self.operator_cloud.image.create_image(
            name=TEST_IMAGE_NAME,
            disk_format='raw',
            container_format='bare',
            properties={
                'description': 'This is not an image',
            },
            data=open('CONTRIBUTING.rst'),
        )
        self.assertIsInstance(self.image, _image.Image)
        self.assertEqual(TEST_IMAGE_NAME, self.image.name)

    def tearDown(self):
        # we do this in tearDown rather than via 'addCleanup' since we want to
        # wait for the deletion of the resource to ensure it completes
        self.operator_cloud.image.delete_image(self.image)
        self.operator_cloud.image.wait_for_delete(self.image)

        super().tearDown()

    def test_images(self):
        # get image
        image = self.operator_cloud.image.get_image(self.image.id)
        self.assertEqual(self.image.name, image.name)

        # find image
        image = self.operator_cloud.image.find_image(self.image.name)
        self.assertEqual(self.image.id, image.id)

        # list
        images = list(self.operator_cloud.image.images())
        # there are many other images so we don't assert that this is the
        # *only* image present
        self.assertIn(self.image.id, {i.id for i in images})

        # update
        image_name = self.getUniqueString()
        image = self.operator_cloud.image.update_image(
            self.image,
            name=image_name,
        )
        self.assertIsInstance(image, _image.Image)
        image = self.operator_cloud.image.get_image(self.image.id)
        self.assertEqual(image_name, image.name)

    def test_tags(self):
        # add tag
        image = self.operator_cloud.image.get_image(self.image)
        self.operator_cloud.image.add_tag(image, 't1')
        self.operator_cloud.image.add_tag(image, 't2')

        # filter image by tags
        image = list(self.operator_cloud.image.images(tag=['t1', 't2']))[0]
        self.assertEqual(image.id, image.id)
        self.assertIn('t1', image.tags)
        self.assertIn('t2', image.tags)

        # remove tag
        self.operator_cloud.image.remove_tag(image, 't1')
        image = self.operator_cloud.image.get_image(self.image)
        self.assertIn('t2', image.tags)
        self.assertNotIn('t1', image.tags)
