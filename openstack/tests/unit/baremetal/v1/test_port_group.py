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

from openstack.baremetal.v1 import port_group

FAKE = {
    "address": "11:11:11:11:11:11",
    "created_at": "2016-08-18T22:28:48.165105+00:00",
    "extra": {},
    "internal_info": {},
    "links": [
        {
            "href": "http://127.0.0.1:6385/v1/portgroups/<PG_ID>",
            "rel": "self"
        },
        {
            "href": "http://127.0.0.1:6385/portgroups/<PG_ID>",
            "rel": "bookmark"
        }
    ],
    "name": "test_portgroup",
    "node_uuid": "6d85703a-565d-469a-96ce-30b6de53079d",
    "ports": [
        {
            "href": "http://127.0.0.1:6385/v1/portgroups/<PG_ID>/ports",
            "rel": "self"
        },
        {
            "href": "http://127.0.0.1:6385/portgroups/<PG_ID>/ports",
            "rel": "bookmark"
        }
    ],
    "standalone_ports_supported": True,
    "updated_at": None,
    "uuid": "e43c722c-248e-4c6e-8ce8-0d8ff129387a",
}


class TestPortGroup(base.TestCase):

    def test_basic(self):
        sot = port_group.PortGroup()
        self.assertIsNone(sot.resource_key)
        self.assertEqual('portgroups', sot.resources_key)
        self.assertEqual('/portgroups', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertEqual('PATCH', sot.commit_method)

    def test_instantiate(self):
        sot = port_group.PortGroup(**FAKE)
        self.assertEqual(FAKE['uuid'], sot.id)
        self.assertEqual(FAKE['address'], sot.address)
        self.assertEqual(FAKE['created_at'], sot.created_at)
        self.assertEqual(FAKE['extra'], sot.extra)
        self.assertEqual(FAKE['internal_info'], sot.internal_info)
        self.assertEqual(FAKE['links'], sot.links)
        self.assertEqual(FAKE['name'], sot.name)
        self.assertEqual(FAKE['node_uuid'], sot.node_id)
        self.assertEqual(FAKE['ports'], sot.ports)
        self.assertEqual(FAKE['standalone_ports_supported'],
                         sot.is_standalone_ports_supported)
        self.assertEqual(FAKE['updated_at'], sot.updated_at)
