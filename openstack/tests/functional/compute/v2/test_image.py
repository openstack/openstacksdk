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


from openstack.compute.v2 import image as _image
from openstack.tests.functional import base
from openstack.tests.functional.image.v2.test_image import TEST_IMAGE_NAME


class TestImage(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()

        # get a non-test image to work with
        images = self.operator_cloud.compute.images()
        self.image = next(images)

        if self.image.name == TEST_IMAGE_NAME:
            self.image = next(images)

    def test_image(self):
        # list all images

        images = list(self.operator_cloud.compute.images())
        self.assertGreater(len(images), 0)
        for image in images:
            self.assertIsInstance(image.id, str)

        # find image by name

        image = self.operator_cloud.compute.find_image(self.image.name)
        self.assertIsInstance(image, _image.Image)
        self.assertEqual(self.image.id, image.id)
        self.assertEqual(self.image.name, image.name)

        # get image by ID

        image = self.operator_cloud.compute.get_image(self.image.id)
        self.assertIsInstance(image, _image.Image)
        self.assertEqual(self.image.id, image.id)
        self.assertEqual(self.image.name, image.name)

    def test_image_metadata(self):
        # delete pre-existing metadata

        self.operator_cloud.compute.delete_image_metadata(
            self.image, self.image.metadata.keys()
        )
        image = self.operator_cloud.compute.get_image_metadata(self.image)
        self.assertFalse(image.metadata)

        # get metadata (should be empty)

        image = self.operator_cloud.compute.get_image_metadata(self.image)
        self.assertFalse(image.metadata)

        # set no metadata

        self.operator_cloud.compute.set_image_metadata(self.image)
        image = self.operator_cloud.compute.get_image_metadata(self.image)
        self.assertFalse(image.metadata)

        # set empty metadata

        self.operator_cloud.compute.set_image_metadata(self.image, k0='')
        image = self.operator_cloud.compute.get_image_metadata(self.image)
        self.assertIn('k0', image.metadata)
        self.assertEqual('', image.metadata['k0'])

        # set metadata

        self.operator_cloud.compute.set_image_metadata(self.image, k1='v1')
        image = self.operator_cloud.compute.get_image_metadata(self.image)
        self.assertTrue(image.metadata)
        self.assertEqual(2, len(image.metadata))
        self.assertIn('k1', image.metadata)
        self.assertEqual('v1', image.metadata['k1'])

        # set more metadata

        self.operator_cloud.compute.set_image_metadata(self.image, k2='v2')
        image = self.operator_cloud.compute.get_image_metadata(self.image)
        self.assertTrue(image.metadata)
        self.assertEqual(3, len(image.metadata))
        self.assertIn('k1', image.metadata)
        self.assertEqual('v1', image.metadata['k1'])
        self.assertIn('k2', image.metadata)
        self.assertEqual('v2', image.metadata['k2'])

        # update metadata

        self.operator_cloud.compute.set_image_metadata(self.image, k1='v1.1')
        image = self.operator_cloud.compute.get_image_metadata(self.image)
        self.assertTrue(image.metadata)
        self.assertEqual(3, len(image.metadata))
        self.assertIn('k1', image.metadata)
        self.assertEqual('v1.1', image.metadata['k1'])
        self.assertIn('k2', image.metadata)
        self.assertEqual('v2', image.metadata['k2'])

        # delete all metadata (cleanup)

        self.operator_cloud.compute.delete_image_metadata(
            self.image, image.metadata.keys()
        )
        image = self.operator_cloud.compute.get_image_metadata(self.image)
        self.assertFalse(image.metadata)
