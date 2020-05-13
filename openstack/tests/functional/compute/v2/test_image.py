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


from openstack.tests.functional import base
from openstack.tests.functional.image.v2.test_image import TEST_IMAGE_NAME


class TestImage(base.BaseFunctionalTest):

    def test_images(self):
        images = list(self.conn.compute.images())
        self.assertGreater(len(images), 0)
        for image in images:
            self.assertIsInstance(image.id, str)

    def _get_non_test_image(self):
        images = self.conn.compute.images()
        image = next(images)

        if image.name == TEST_IMAGE_NAME:
            image = next(images)

        return image

    def test_find_image(self):
        image = self._get_non_test_image()
        self.assertIsNotNone(image)
        sot = self.conn.compute.find_image(image.id)
        self.assertEqual(image.id, sot.id)
        self.assertEqual(image.name, sot.name)

    def test_get_image(self):
        image = self._get_non_test_image()
        self.assertIsNotNone(image)
        sot = self.conn.compute.get_image(image.id)
        self.assertEqual(image.id, sot.id)
        self.assertEqual(image.name, sot.name)
        self.assertIsNotNone(image.links)
        self.assertIsNotNone(image.min_disk)
        self.assertIsNotNone(image.min_ram)
        self.assertIsNotNone(image.metadata)
        self.assertIsNotNone(image.progress)
        self.assertIsNotNone(image.status)

    def test_image_metadata(self):
        image = self._get_non_test_image()

        # delete pre-existing metadata
        self.conn.compute.delete_image_metadata(image, image.metadata.keys())
        image = self.conn.compute.get_image_metadata(image)
        self.assertFalse(image.metadata)

        # get metadata
        image = self.conn.compute.get_image_metadata(image)
        self.assertFalse(image.metadata)

        # set no metadata
        self.conn.compute.set_image_metadata(image)
        image = self.conn.compute.get_image_metadata(image)
        self.assertFalse(image.metadata)

        # set empty metadata
        self.conn.compute.set_image_metadata(image, k0='')
        image = self.conn.compute.get_image_metadata(image)
        self.assertIn('k0', image.metadata)
        self.assertEqual('', image.metadata['k0'])

        # set metadata
        self.conn.compute.set_image_metadata(image, k1='v1')
        image = self.conn.compute.get_image_metadata(image)
        self.assertTrue(image.metadata)
        self.assertEqual(2, len(image.metadata))
        self.assertIn('k1', image.metadata)
        self.assertEqual('v1', image.metadata['k1'])

        # set more metadata
        self.conn.compute.set_image_metadata(image, k2='v2')
        image = self.conn.compute.get_image_metadata(image)
        self.assertTrue(image.metadata)
        self.assertEqual(3, len(image.metadata))
        self.assertIn('k1', image.metadata)
        self.assertEqual('v1', image.metadata['k1'])
        self.assertIn('k2', image.metadata)
        self.assertEqual('v2', image.metadata['k2'])

        # update metadata
        self.conn.compute.set_image_metadata(image, k1='v1.1')
        image = self.conn.compute.get_image_metadata(image)
        self.assertTrue(image.metadata)
        self.assertEqual(3, len(image.metadata))
        self.assertIn('k1', image.metadata)
        self.assertEqual('v1.1', image.metadata['k1'])
        self.assertIn('k2', image.metadata)
        self.assertEqual('v2', image.metadata['k2'])

        # delete metadata
        self.conn.compute.delete_image_metadata(image, image.metadata.keys())
        image = self.conn.compute.get_image_metadata(image)
        self.assertFalse(image.metadata)
