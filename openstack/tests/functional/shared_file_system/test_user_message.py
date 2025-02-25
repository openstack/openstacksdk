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


class UserMessageTest(base.BaseSharedFileSystemTest):
    def test_user_messages(self):
        # TODO(kafilat): We must intentionally cause an asynchronous failure to
        # ensure that at least one user message exists;
        u_messages = self.user_cloud.shared_file_system.user_messages()
        # self.assertGreater(len(list(u_messages)), 0)
        for u_message in u_messages:
            for attribute in (
                'id',
                'created_at',
                'action_id',
                'detail_id',
                'expires_at',
                'message_level',
                'project_id',
                'request_id',
                'resource_id',
                'resource_type',
                'user_message',
            ):
                self.assertTrue(hasattr(u_message, attribute))
                self.assertIsInstance(getattr(u_message, attribute), str)

            self.operator_cloud.shared_file_system.delete_user_message(
                u_message
            )
