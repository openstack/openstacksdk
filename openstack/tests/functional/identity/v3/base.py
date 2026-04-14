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

from openstack.identity.v3 import _proxy as _identity_v3
from openstack.tests.functional import base
from openstack import utils


class BaseIdentityTest(base.BaseFunctionalTest):
    admin_identity_client: _identity_v3.Proxy
    system_admin_identity_client: _identity_v3.Proxy

    def setUp(self):
        super().setUp()
        # FIXME(stephenfin) This is causing our tests to be skipped. Why?
        # if not self.operator_cloud.has_service('identity', '3'):
        #     self.skipTest('identity service not supported by cloud')

        self.admin_identity_client = utils.ensure_service_version(
            self.operator_cloud.identity, '3'
        )
        self.system_admin_identity_client = utils.ensure_service_version(
            self.system_admin_cloud.identity, '3'
        )
