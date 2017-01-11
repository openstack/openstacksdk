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

import os

import os_client_config as occ

import shade
from shade.tests import base


class BaseFunctionalTestCase(base.TestCase):
    def setUp(self):
        super(BaseFunctionalTestCase, self).setUp()

        demo_name = os.environ.get('SHADE_DEMO_CLOUD', 'devstack')
        op_name = os.environ.get('SHADE_OPERATOR_CLOUD', 'devstack-admin')

        self.config = occ.OpenStackConfig()
        demo_config = self.config.get_one_cloud(cloud=demo_name)
        self.demo_cloud = shade.OpenStackCloud(
            cloud_config=demo_config,
            log_inner_exceptions=True)
        operator_config = self.config.get_one_cloud(cloud=op_name)
        self.operator_cloud = shade.OperatorCloud(
            cloud_config=operator_config,
            log_inner_exceptions=True)

        self.identity_version = \
            self.operator_cloud.cloud_config.get_api_version('identity')
