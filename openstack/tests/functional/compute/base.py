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

from openstack.tests.functional import base


class BaseComputeTest(base.BaseFunctionalTest):

    @classmethod
    def setUpClass(cls):
        super(BaseComputeTest, cls).setUpClass()
        cls._wait_for_timeout = int(os.getenv(
            'OPENSTACKSDK_FUNC_TEST_TIMEOUT_COMPUTE',
            cls._wait_for_timeout))
