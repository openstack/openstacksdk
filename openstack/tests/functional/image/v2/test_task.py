# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from http import HTTPStatus

from openstack import exceptions
from openstack.tests.functional.image.v2 import base


class TestTask(base.BaseImageTest):
    def test_tasks(self):
        try:
            tasks = list(self.admin_image_client.tasks())
        except exceptions.HttpException as error:
            # The deprecated global Tasks API returns 410 Gone. Consumers
            # should use the interoperable image import API instead.
            self.assertEqual(HTTPStatus.GONE, error.status_code)
        else:
            self.assertIsInstance(tasks, list)
