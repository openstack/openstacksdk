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


class BaseBlockStorageTest(base.BaseFunctionalTest):
    _wait_for_timeout_key = 'OPENSTACKSDK_FUNC_TEST_TIMEOUT_BLOCK_STORAGE'

    def setUp(self):
        super().setUp()
        self._set_user_cloud(block_storage_api_version='2')
        self._set_operator_cloud(block_storage_api_version='2')

        if not self.user_cloud.has_service('block-storage', '2'):
            self.skipTest('block-storage service not supported by cloud')
