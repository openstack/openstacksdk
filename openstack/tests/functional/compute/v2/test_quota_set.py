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


class TestQS(base.BaseFunctionalTest):
    def test_qs(self):
        sot = self.conn.compute.get_quota_set(self.conn.current_project_id)
        self.assertIsNotNone(sot.key_pairs)

    def test_qs_user(self):
        sot = self.conn.compute.get_quota_set(
            self.conn.current_project_id,
            user_id=self.conn.session.auth.get_user_id(self.conn.compute),
        )
        self.assertIsNotNone(sot.key_pairs)

    def test_update(self):
        sot = self.conn.compute.get_quota_set(self.conn.current_project_id)
        self.conn.compute.update_quota_set(
            sot,
            query={
                'user_id': self.conn.session.auth.get_user_id(
                    self.conn.compute
                )
            },
            key_pairs=100,
        )

    def test_revert(self):
        self.conn.compute.revert_quota_set(
            self.conn.current_project_id,
            user_id=self.conn.session.auth.get_user_id(self.conn.compute),
        )
