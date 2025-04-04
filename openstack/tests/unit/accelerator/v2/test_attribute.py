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

from openstack.accelerator.v2 import attribute
from openstack.tests.unit import base


FAKE = {
    "id": 1,
    "uuid": "a95e10ae-b3e3-4eab-a513-1afae6f17c51",
    "deployable_id": 1,
    "key": "traits1",
    'value': 'CUSTOM_FAKE_DEVICE',
}


class TestAttribute(base.TestCase):
    def test_basic(self):
        sot = attribute.Attribute()
        self.assertEqual('attribute', sot.resource_key)
        self.assertEqual('attributes', sot.resources_key)
        self.assertEqual('/attributes', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertFalse(sot.allow_patch)

    def test_make_it(self):
        sot = attribute.Attribute(**FAKE)
        self.assertEqual(FAKE['id'], sot.id)
        self.assertEqual(FAKE['uuid'], sot.uuid)
        self.assertEqual(FAKE['deployable_id'], sot.deployable_id)
        self.assertEqual(FAKE['key'], sot.key)
        self.assertEqual(FAKE['value'], sot.value)
