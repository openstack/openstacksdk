# -*- coding: utf-8 -*-

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

"""
test_compute
----------------------------------

Functional tests for `shade` image methods.
"""

import tempfile
import uuid

from shade import openstack_cloud
from shade.tests import base
from shade.tests.functional.util import pick_image


class TestImage(base.TestCase):
    def setUp(self):
        super(TestImage, self).setUp()
        self.cloud = openstack_cloud(cloud='devstack')
        self.image = pick_image(self.cloud.nova_client.images.list())

    def test_create_image(self):
        test_image = tempfile.NamedTemporaryFile(delete=False)
        test_image.write('\0' * 1024 * 1024)
        test_image.close()
        image_name = 'test-image-%s' % uuid.uuid4()
        try:
            self.cloud.create_image(name=image_name,
                                    filename=test_image.name,
                                    disk_format='raw',
                                    container_format='bare',
                                    wait=True)
        finally:
            self.cloud.delete_image(image_name, wait=True)
