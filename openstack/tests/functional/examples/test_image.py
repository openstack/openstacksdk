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

from examples.image import create as image_create
from examples.image import delete as image_delete
from examples.image import list as image_list

from openstack.tests.functional import base


class TestImage(base.BaseFunctionalTest):
    """Test the image examples

    The purpose of these tests is to ensure the examples run successfully.
    """

    def test_image(self):
        image_list.list_images(self.operator_cloud)

        image_create.upload_image(self.operator_cloud)

        image_delete.delete_image(self.operator_cloud)
