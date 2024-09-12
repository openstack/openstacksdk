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

from openstack.key_manager.v1 import order
from openstack.tests.unit import base


ID_VAL = "123"
SECRET_ID = "5"
IDENTIFIER = f'http://localhost/orders/{ID_VAL}'
EXAMPLE = {
    'created': '1',
    'creator_id': '2',
    'meta': {'key': '3'},
    'order_ref': IDENTIFIER,
    'secret_ref': f'http://localhost/secrets/{SECRET_ID}',
    'status': '6',
    'sub_status': '7',
    'sub_status_message': '8',
    'type': '9',
    'updated': '10',
}


class TestOrder(base.TestCase):
    def test_basic(self):
        sot = order.Order()
        self.assertIsNone(sot.resource_key)
        self.assertEqual('orders', sot.resources_key)
        self.assertEqual('/orders', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = order.Order(**EXAMPLE)
        self.assertEqual(EXAMPLE['created'], sot.created_at)
        self.assertEqual(EXAMPLE['creator_id'], sot.creator_id)
        self.assertEqual(EXAMPLE['meta'], sot.meta)
        self.assertEqual(EXAMPLE['order_ref'], sot.order_ref)
        self.assertEqual(ID_VAL, sot.order_id)
        self.assertEqual(EXAMPLE['secret_ref'], sot.secret_ref)
        self.assertEqual(SECRET_ID, sot.secret_id)
        self.assertEqual(EXAMPLE['status'], sot.status)
        self.assertEqual(EXAMPLE['sub_status'], sot.sub_status)
        self.assertEqual(EXAMPLE['sub_status_message'], sot.sub_status_message)
        self.assertEqual(EXAMPLE['type'], sot.type)
        self.assertEqual(EXAMPLE['updated'], sot.updated_at)
