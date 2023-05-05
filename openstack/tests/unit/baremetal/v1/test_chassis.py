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

from openstack.baremetal.v1 import chassis
from openstack.tests.unit import base


FAKE = {
    "created_at": "2016-08-18T22:28:48.165105+00:00",
    "description": "Sample chassis",
    "extra": {},
    "links": [
        {"href": "http://127.0.0.1:6385/v1/chassis/ID", "rel": "self"},
        {"href": "http://127.0.0.1:6385/chassis/ID", "rel": "bookmark"},
    ],
    "nodes": [
        {"href": "http://127.0.0.1:6385/v1/chassis/ID/nodes", "rel": "self"},
        {"href": "http://127.0.0.1:6385/chassis/ID/nodes", "rel": "bookmark"},
    ],
    "updated_at": None,
    "uuid": "dff29d23-1ded-43b4-8ae1-5eebb3e30de1",
}


class TestChassis(base.TestCase):
    def test_basic(self):
        sot = chassis.Chassis()
        self.assertIsNone(sot.resource_key)
        self.assertEqual('chassis', sot.resources_key)
        self.assertEqual('/chassis', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertEqual('PATCH', sot.commit_method)

    def test_instantiate(self):
        sot = chassis.Chassis(**FAKE)
        self.assertEqual(FAKE['uuid'], sot.id)
        self.assertEqual(FAKE['created_at'], sot.created_at)
        self.assertEqual(FAKE['description'], sot.description)
        self.assertEqual(FAKE['extra'], sot.extra)
        self.assertEqual(FAKE['links'], sot.links)
        self.assertEqual(FAKE['nodes'], sot.nodes)
        self.assertEqual(FAKE['updated_at'], sot.updated_at)
