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
import uuid

from openstack.tests.unit import base
from openstack.accelerator.v2 import device

EXAMPLE = {
    'id': '1',
    'uuid': uuid.uuid4(),
    'created_at': '2019-08-09T12:14:57.233772',
    'updated_at': '2019-08-09T12:15:57.233772',
    'type': 'test_type',
    'vendor': '0x8086',
    'model': 'test_model',
    'std_board_info': '{"product_id": "0x09c4"}',
    'vendor_board_info': 'test_vb_info',
}


class TestDevice(base.TestCase):

    def test_basic(self):
        sot = device.Device()
        self.assertEqual('device', sot.resource_key)
        self.assertEqual('devices', sot.resources_key)
        self.assertEqual('/devices', sot.base_path)
        self.assertFalse(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = device.Device(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['uuid'], sot.uuid)
        self.assertEqual(EXAMPLE['type'], sot.type)
        self.assertEqual(EXAMPLE['vendor'], sot.vendor)
        self.assertEqual(EXAMPLE['model'], sot.model)
        self.assertEqual(EXAMPLE['std_board_info'], sot.std_board_info)
        self.assertEqual(EXAMPLE['vendor_board_info'], sot.vendor_board_info)
        self.assertEqual(EXAMPLE['created_at'], sot.created_at)
        self.assertEqual(EXAMPLE['updated_at'], sot.updated_at)
