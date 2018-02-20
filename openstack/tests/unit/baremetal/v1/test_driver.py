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

from openstack.baremetal.v1 import driver

FAKE = {
    "hosts": [
        "897ab1dad809"
    ],
    "links": [
        {
            "href": "http://127.0.0.1:6385/v1/drivers/agent_ipmitool",
            "rel": "self"
        },
        {
            "href": "http://127.0.0.1:6385/drivers/agent_ipmitool",
            "rel": "bookmark"
        }
    ],
    "name": "agent_ipmitool",
    "properties": [
        {
            "href":
                "http://127.0.0.1:6385/v1/drivers/agent_ipmitool/properties",
            "rel": "self"
        },
        {
            "href": "http://127.0.0.1:6385/drivers/agent_ipmitool/properties",
            "rel": "bookmark"
        }
    ]
}


class TestDriver(base.TestCase):

    def test_basic(self):
        sot = driver.Driver()
        self.assertIsNone(sot.resource_key)
        self.assertEqual('drivers', sot.resources_key)
        self.assertEqual('/drivers', sot.base_path)
        self.assertEqual('baremetal', sot.service.service_type)
        self.assertFalse(sot.allow_create)
        self.assertTrue(sot.allow_get)
        self.assertFalse(sot.allow_update)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_instantiate(self):
        sot = driver.Driver(**FAKE)
        self.assertEqual(FAKE['name'], sot.id)
        self.assertEqual(FAKE['name'], sot.name)
        self.assertEqual(FAKE['hosts'], sot.hosts)
        self.assertEqual(FAKE['links'], sot.links)
        self.assertEqual(FAKE['properties'], sot.properties)
