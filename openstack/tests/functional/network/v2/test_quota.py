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
        for qot in self.conn.network.quotas():
            self.assertIsNotNone(qot.project_id)
            self.assertIsNotNone(qot.networks)

    def test_list_details(self):
        expected_keys = ['limit', 'used', 'reserved']
        project_id = self.conn.session.get_project_id()
        quota_details = self.conn.network.get_quota(project_id, details=True)
        for details in quota_details._body.attributes.values():
            for expected_key in expected_keys:
                self.assertTrue(expected_key in details.keys())

    def test_set(self):
        attrs = {'networks': 123456789}
        for project_quota in self.conn.network.quotas():
            self.conn.network.update_quota(project_quota, **attrs)
            new_quota = self.conn.network.get_quota(project_quota.project_id)
            self.assertEqual(123456789, new_quota.networks)
