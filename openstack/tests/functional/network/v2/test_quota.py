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


class TestQuota(base.BaseFunctionalTest):

    def test_list(self):
        sot = self.conn.network.quotas()
        for qot in sot:
            self.assertIn('subnet', qot)
            self.assertIn('network', qot)
            self.assertIn('router', qot)
            self.assertIn('port', qot)
            self.assertIn('floatingip', qot)
            self.assertIn('security_group_rule', qot)
            self.assertIn('security_group', qot)
            self.assertIn('subnetpool', qot)
            self.assertIn('rbac_policy', qot)
