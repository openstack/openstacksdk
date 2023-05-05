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

from openstack.tests.functional.shared_file_system import base


class AvailabilityZoneTest(base.BaseSharedFileSystemTest):
    min_microversion = '2.7'

    def test_availability_zones(self):
        azs = self.user_cloud.shared_file_system.availability_zones()
        self.assertGreater(len(list(azs)), 0)
        for az in azs:
            for attribute in ('id', 'name', 'created_at', 'updated_at'):
                self.assertTrue(hasattr(az, attribute))
                self.assertIsInstance(getattr(az, attribute), 'str')
