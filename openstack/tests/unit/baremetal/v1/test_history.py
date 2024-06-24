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

from typing import Any

from openstack.baremetal.v1 import history
from openstack.tests.unit import base

NODE_ID = "12345678-aaaa-5856-bfb6-6aaaacd3dd11"
EVENT_ID = "0bcdde1c-36a0-4296-9ca7-f654673dfbb3"
EVENT_LINK = {
    "href": f"http://127.0.0.1:6385/v1/nodes/{NODE_ID}/history/{EVENT_ID}",
    "rel": "self",
}

# Item as returned by GET /v1/nodes/{node}/history
FAKE_LIST_ITEM: dict[str, Any] = {
    "uuid": EVENT_ID,
    "created_at": "2024-06-12T21:54:37+00:00",
    "severity": "ERROR",
    "event": (
        "Failed to change power state to 'power on' by 'rebooting': "
        "Failed to set node power state to power on."
    ),
    "links": [EVENT_LINK],
}

# Response of GET /v1/nodes/{node}/history/{event}
FAKE: dict[str, Any] = {
    **FAKE_LIST_ITEM,
    "event_type": "UNKNOWN",
    "conductor": "u640-u04",
    "user": None,
    "project": "5b5b6d0c1c9a4bd6a2a8e6c9a1d1f0aa",
    "state": "active",
    "target_provision_state": None,
    "duration_seconds": 12.5,
}


class TestHistory(base.TestCase):
    def test_basic(self):
        sot = history.History()
        self.assertEqual('history', sot.resources_key)
        self.assertIsNone(sot.resource_key)
        self.assertEqual('/nodes/%(node_id)s/history', sot.base_path)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_list)
        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.allow_commit)
        self.assertFalse(sot.allow_delete)

    def test_instantiate(self):
        sot = history.History(node_id=NODE_ID, **FAKE)
        self.assertEqual(FAKE['uuid'], sot.id)
        self.assertEqual(FAKE['created_at'], sot.created_at)
        self.assertEqual(FAKE['severity'], sot.severity)
        self.assertEqual(FAKE['event'], sot.event)
        self.assertEqual(FAKE['event_type'], sot.event_type)
        self.assertEqual(FAKE['conductor'], sot.conductor)
        self.assertIsNone(sot.user)
        self.assertEqual(FAKE['project'], sot.project)
        self.assertEqual(FAKE['state'], sot.state)
        self.assertIsNone(sot.target_provision_state)
        self.assertEqual(FAKE['duration_seconds'], sot.duration_seconds)
        self.assertEqual(NODE_ID, sot.node_id)

    def test_query_mapping(self):
        sot = history.History()
        self.assertEqual(
            {
                'detail': 'detail',
                'limit': 'limit',
                'marker': 'marker',
                'sort_key': 'sort_key',
                'sort_dir': 'sort_dir',
            },
            sot._query_mapping._mapping,
        )

    def test_request_urls(self):
        # The event is addressed as /nodes/{node_id}/history/{event_uuid},
        # where the event UUID is the resource ID
        sot = history.History(node_id=NODE_ID, **FAKE)
        self.assertEqual(
            f'nodes/{NODE_ID}/history/{EVENT_ID}',
            sot._prepare_request(requires_id=True).url,
        )
        self.assertEqual(
            f'/nodes/{NODE_ID}/history',
            sot._prepare_request(requires_id=False).url,
        )

    def test_instantiate_list_item(self):
        # The list response only carries a subset of the fields
        sot = history.History(node_id=NODE_ID, **FAKE_LIST_ITEM)
        self.assertEqual(FAKE_LIST_ITEM['uuid'], sot.id)
        self.assertEqual(FAKE_LIST_ITEM['created_at'], sot.created_at)
        self.assertEqual(FAKE_LIST_ITEM['severity'], sot.severity)
        self.assertEqual(FAKE_LIST_ITEM['event'], sot.event)
        self.assertIsNone(sot.event_type)
        self.assertIsNone(sot.conductor)
        self.assertIsNone(sot.user)
        self.assertEqual(NODE_ID, sot.node_id)
