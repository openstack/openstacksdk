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

from openstack.block_storage.v3 import _proxy as _block_storage_proxy
from openstack.compute.v2 import _proxy as _compute_proxy
from openstack.tests.functional import base
from openstack import utils


class BaseComputeTest(base.BaseFunctionalTest):
    _wait_for_timeout_key = 'OPENSTACKSDK_FUNC_TEST_TIMEOUT_COMPUTE'

    admin_compute_client: _compute_proxy.Proxy
    compute_client: _compute_proxy.Proxy

    admin_block_storage_client: _block_storage_proxy.Proxy
    block_storage_client: _block_storage_proxy.Proxy

    def setUp(self):
        super().setUp()
        self._set_user_cloud(compute_api_version='2')
        if not self.user_cloud.has_service('compute', '2'):
            self.skipTest('compute service not supported by cloud')

        self.admin_compute_client = utils.ensure_service_version(
            self.operator_cloud.compute, '2'
        )
        self.compute_client = utils.ensure_service_version(
            self.user_cloud.compute, '2'
        )

        if not self.user_cloud.has_service('block-storage', '3'):
            self.skipTest('block-storage service not supported by cloud')

        self.admin_block_storage_client = utils.ensure_service_version(
            self.operator_cloud.block_storage, '3'
        )
        self.block_storage_client = utils.ensure_service_version(
            self.user_cloud.block_storage, '3'
        )
