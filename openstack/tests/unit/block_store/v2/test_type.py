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

import testtools

from openstack.block_store.v2 import type

FAKE_ID = "6685584b-1eac-4da6-b5c3-555430cf68ff"
TYPE = {
    "extra_specs": {
        "capabilities": "gpu"
    },
    "id": FAKE_ID,
    "name": "SSD"
}


class TestType(testtools.TestCase):

    def test_basic(self):
        sot = type.Type(TYPE)
        self.assertEqual("volume_type", sot.resource_key)
        self.assertEqual("volume_types", sot.resources_key)
        self.assertEqual("id", sot.id_attribute)
        self.assertEqual("/types", sot.base_path)
        self.assertEqual("volume", sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_delete)
        self.assertFalse(sot.allow_list)

    def test_new(self):
        sot = type.Type.new(id=FAKE_ID)
        self.assertEqual(FAKE_ID, sot.id)

    def test_create(self):
        sot = type.Type(TYPE)
        self.assertEqual(TYPE["id"], sot.id)
        self.assertEqual(TYPE["extra_specs"], sot.extra_specs)
        self.assertEqual(TYPE["name"], sot.name)
