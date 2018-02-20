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

from openstack.baremetal.v1 import port

FAKE = {
    "address": "11:11:11:11:11:11",
    "created_at": "2016-08-18T22:28:49.946416+00:00",
    "extra": {},
    "internal_info": {},
    "links": [
        {
            "href": "http://127.0.0.1:6385/v1/ports/<PORT_ID>",
            "rel": "self"
        },
        {
            "href": "http://127.0.0.1:6385/ports/<PORT_ID>",
            "rel": "bookmark"
        }
    ],
    "local_link_connection": {
        "port_id": "Ethernet3/1",
        "switch_id": "0a:1b:2c:3d:4e:5f",
        "switch_info": "switch1"
    },
    "node_uuid": "6d85703a-565d-469a-96ce-30b6de53079d",
    "portgroup_uuid": "e43c722c-248e-4c6e-8ce8-0d8ff129387a",
    "pxe_enabled": True,
    "updated_at": None,
    "uuid": "d2b30520-907d-46c8-bfee-c5586e6fb3a1"
}


class TestPort(base.TestCase):

    def test_basic(self):
        sot = port.Port()
        self.assertIsNone(sot.resource_key)
        self.assertEqual('ports', sot.resources_key)
        self.assertEqual('/ports', sot.base_path)
        self.assertEqual('baremetal', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_get)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertEqual('PATCH', sot.update_method)

    def test_instantiate(self):
        sot = port.PortDetail(**FAKE)
        self.assertEqual(FAKE['uuid'], sot.id)
        self.assertEqual(FAKE['address'], sot.address)
        self.assertEqual(FAKE['created_at'], sot.created_at)
        self.assertEqual(FAKE['extra'], sot.extra)
        self.assertEqual(FAKE['internal_info'], sot.internal_info)
        self.assertEqual(FAKE['links'], sot.links)
        self.assertEqual(FAKE['local_link_connection'],
                         sot.local_link_connection)
        self.assertEqual(FAKE['node_uuid'], sot.node_id)
        self.assertEqual(FAKE['portgroup_uuid'], sot.port_group_id)
        self.assertEqual(FAKE['pxe_enabled'], sot.is_pxe_enabled)
        self.assertEqual(FAKE['updated_at'], sot.updated_at)


class TestPortDetail(base.TestCase):

    def test_basic(self):
        sot = port.PortDetail()
        self.assertIsNone(sot.resource_key)
        self.assertEqual('ports', sot.resources_key)
        self.assertEqual('/ports/detail', sot.base_path)
        self.assertEqual('baremetal', sot.service.service_type)
        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.allow_get)
        self.assertFalse(sot.allow_update)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_instantiate(self):
        sot = port.PortDetail(**FAKE)
        self.assertEqual(FAKE['uuid'], sot.id)
        self.assertEqual(FAKE['address'], sot.address)
        self.assertEqual(FAKE['created_at'], sot.created_at)
        self.assertEqual(FAKE['extra'], sot.extra)
        self.assertEqual(FAKE['internal_info'], sot.internal_info)
        self.assertEqual(FAKE['links'], sot.links)
        self.assertEqual(FAKE['local_link_connection'],
                         sot.local_link_connection)
        self.assertEqual(FAKE['node_uuid'], sot.node_id)
        self.assertEqual(FAKE['portgroup_uuid'], sot.port_group_id)
        self.assertEqual(FAKE['pxe_enabled'], sot.is_pxe_enabled)
        self.assertEqual(FAKE['updated_at'], sot.updated_at)
