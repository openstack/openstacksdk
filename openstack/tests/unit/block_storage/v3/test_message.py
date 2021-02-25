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

from openstack.block_storage.v3 import message
from openstack.tests.unit import base

MESSAGE = {
    "request_id": "req-c1216709-afba-4703-a1a3-22eda88f2f5a",
    "links": [
        {"href": "http://localhost:8776/link1", "rel": "self"},
        {"href": "http://localhost:8776/link2", "rel": "bookmark"},
    ],
    "message_level": "ERROR",
    "event_id": "VOLUME_000002",
    "created_at": "2021-02-25T00:00:00-00:00",
    "guaranteed_until": "2021-02-26T00:00:00-00:00",
    "resource_uuid": "d5f6c517-c3e8-45fe-b994-b11118e4cacf",
    "id": "c506cd4b-9048-43bc-97ef-0d7dec369b42",
    "resource_type": "VOLUME",
    "user_message": "Test message.",
}


class TestMessage(base.TestCase):
    def test_basic(self):
        message_resource = message.Message()
        self.assertEqual('messages', message_resource.resource_key)
        self.assertEqual('messages', message_resource.resources_key)
        self.assertEqual('/messages', message_resource.base_path)
        self.assertTrue(message_resource.allow_fetch)
        self.assertFalse(message_resource.allow_create)
        self.assertFalse(message_resource.allow_commit)
        self.assertTrue(message_resource.allow_delete)
        self.assertTrue(message_resource.allow_list)

    def test_make_message(self):
        message_resource = message.Message(**MESSAGE)
        self.assertEqual(MESSAGE['request_id'], message_resource.request_id)
        self.assertEqual(
            MESSAGE['message_level'], message_resource.message_level
        )
        self.assertEqual(MESSAGE['event_id'], message_resource.event_id)
        self.assertEqual(MESSAGE['created_at'], message_resource.created_at)
        self.assertEqual(
            MESSAGE['guaranteed_until'], message_resource.guaranteed_until
        )
        self.assertEqual(
            MESSAGE['resource_uuid'], message_resource.resource_uuid
        )
        self.assertEqual(MESSAGE['id'], message_resource.id)
        self.assertEqual(
            MESSAGE['resource_type'], message_resource.resource_type
        )
        self.assertEqual(
            MESSAGE['user_message'], message_resource.user_message
        )
