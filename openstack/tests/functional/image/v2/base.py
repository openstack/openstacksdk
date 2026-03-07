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

from openstack.image.v2 import _proxy as _image_v2
from openstack.tests.functional import base
from openstack import utils


class BaseImageTest(base.BaseFunctionalTest):
    _wait_for_timeout_key = 'OPENSTACKSDK_FUNC_TEST_TIMEOUT_IMAGE'

    admin_image_client: _image_v2.Proxy
    image_client: _image_v2.Proxy

    def setUp(self):
        super().setUp()
        self._set_user_cloud(image_api_version='2')
        self._set_operator_cloud(image_api_version='2')

        if not self.user_cloud.has_service('image', '2'):
            self.skipTest('image service not supported by cloud')
        self.admin_image_client = utils.ensure_service_version(
            self.operator_cloud.image, '2'
        )
        self.image_client = utils.ensure_service_version(
            self.user_cloud.image, '2'
        )
