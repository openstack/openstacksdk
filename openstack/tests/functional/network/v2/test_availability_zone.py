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


class TestAvailabilityZone(base.BaseFunctionalTest):

    def test_list(self):
        availability_zones = list(self.conn.network.availability_zones())
        self.assertGreater(len(availability_zones), 0)

        for az in availability_zones:
            self.assertIsInstance(az.name, str)
            self.assertIsInstance(az.resource, str)
            self.assertIsInstance(az.state, str)
