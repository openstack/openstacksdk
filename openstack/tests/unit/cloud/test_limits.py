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

from openstack.tests.unit import base


class TestLimits(base.TestCase):

    def test_get_compute_limits(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['limits']),
                 json={
                     "limits": {
                         "absolute": {
                             "maxImageMeta": 128,
                             "maxPersonality": 5,
                             "maxPersonalitySize": 10240,
                             "maxSecurityGroupRules": 20,
                             "maxSecurityGroups": 10,
                             "maxServerMeta": 128,
                             "maxTotalCores": 20,
                             "maxTotalFloatingIps": 10,
                             "maxTotalInstances": 10,
                             "maxTotalKeypairs": 100,
                             "maxTotalRAMSize": 51200,
                             "maxServerGroups": 10,
                             "maxServerGroupMembers": 10,
                             "totalCoresUsed": 0,
                             "totalInstancesUsed": 0,
                             "totalRAMUsed": 0,
                             "totalSecurityGroupsUsed": 0,
                             "totalFloatingIpsUsed": 0,
                             "totalServerGroupsUsed": 0
                         },
                         "rate": []
                     }
                 }),
        ])

        self.cloud.get_compute_limits()

        self.assert_calls()

    def test_other_get_compute_limits(self):
        project = self.mock_for_keystone_projects(project_count=1,
                                                  list_get=True)[0]
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['limits'],
                     qs_elements=[
                         'tenant_id={id}'.format(id=project.project_id)
                     ]),
                 json={
                     "limits": {
                         "absolute": {
                             "maxImageMeta": 128,
                             "maxPersonality": 5,
                             "maxPersonalitySize": 10240,
                             "maxSecurityGroupRules": 20,
                             "maxSecurityGroups": 10,
                             "maxServerMeta": 128,
                             "maxTotalCores": 20,
                             "maxTotalFloatingIps": 10,
                             "maxTotalInstances": 10,
                             "maxTotalKeypairs": 100,
                             "maxTotalRAMSize": 51200,
                             "maxServerGroups": 10,
                             "maxServerGroupMembers": 10,
                             "totalCoresUsed": 0,
                             "totalInstancesUsed": 0,
                             "totalRAMUsed": 0,
                             "totalSecurityGroupsUsed": 0,
                             "totalFloatingIpsUsed": 0,
                             "totalServerGroupsUsed": 0
                         },
                         "rate": []
                     }
                 }),
        ])

        self.cloud.get_compute_limits(project.project_id)

        self.assert_calls()
