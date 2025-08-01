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


class TestService(base.BaseFunctionalTest):
    def test_service(self):
        # list all services
        services = list(self.operator_cloud.compute.services())
        self.assertIsNotNone(services)

        # find a service
        self.operator_cloud.compute.find_service(
            services[0].name, host=services[0].host, ignore_missing=False
        )
