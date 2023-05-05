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

from openstack.shared_file_system.v2 import user_message
from openstack.tests.unit import base


IDENTIFIER = "2784bc88-b729-4220-a6bb-a8b7a8f53aad"
EXAMPLE = {
    "id": IDENTIFIER,
    "project_id": "dcc9de3c5fc8471ba3662dbb2b6166d5",
    "action_id": "001",
    "detail_id": "008",
    "message_level": "ERROR",
    "created_at": "2021-03-26T05:16:39.000000",
    "expires_at": "2021-04-25T05:16:39.000000",
    "request_id": "req-e4b3e6de-ce4d-4ef2-b1e7-0087200e4db3",
    "resource_type": "SHARE",
    "resource_id": "c2e4ca07-8c37-4014-92c9-2171c7813fa0",
    "user_message": (
        "allocate host: No storage could be allocated"
        "for this share request, Capabilities filter"
        "didn't succeed."
    ),
}


class TestUserMessage(base.TestCase):
    def test_basic(self):
        message = user_message.UserMessage()
        self.assertEqual('messages', message.resources_key)
        self.assertEqual('/messages', message.base_path)
        self.assertTrue(message.allow_list)
        self.assertFalse(message.allow_create)
        self.assertFalse(message.allow_commit)
        self.assertTrue(message.allow_delete)
        self.assertTrue(message.allow_fetch)
        self.assertFalse(message.allow_head)

        self.assertDictEqual(
            {"limit": "limit", "marker": "marker", "message_id": "message_id"},
            message._query_mapping._mapping,
        )

    def test_user_message(self):
        messages = user_message.UserMessage(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], messages.id)
        self.assertEqual(EXAMPLE['resource_id'], messages.resource_id)
        self.assertEqual(EXAMPLE['message_level'], messages.message_level)
        self.assertEqual(EXAMPLE['user_message'], messages.user_message)
        self.assertEqual(EXAMPLE['expires_at'], messages.expires_at)
        self.assertEqual(EXAMPLE['detail_id'], messages.detail_id)
        self.assertEqual(EXAMPLE['created_at'], messages.created_at)
        self.assertEqual(EXAMPLE['request_id'], messages.request_id)
        self.assertEqual(EXAMPLE['project_id'], messages.project_id)
        self.assertEqual(EXAMPLE['resource_type'], messages.resource_type)
        self.assertEqual(EXAMPLE['action_id'], messages.action_id)
