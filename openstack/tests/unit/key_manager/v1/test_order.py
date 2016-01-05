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

from openstack.key_manager.v1 import order

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'error_reason': '1',
    'error_status_code': '2',
    'meta': '3',
    'order_ref': '4',
    'secret_ref': '5',
    'status': '6',
    'type': '7',
}


class TestOrder(testtools.TestCase):

    def test_basic(self):
        sot = order.Order()
        self.assertIsNone(sot.resource_key)
        self.assertEqual('orders', sot.resources_key)
        self.assertEqual('/orders', sot.base_path)
        self.assertEqual('key-manager', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = order.Order(EXAMPLE)
        self.assertEqual(EXAMPLE['error_reason'], sot.error_reason)
        self.assertEqual(EXAMPLE['error_status_code'], sot.error_status_code)
        self.assertEqual(EXAMPLE['meta'], sot.meta)
        self.assertEqual(EXAMPLE['order_ref'], sot.order_ref)
        self.assertEqual(EXAMPLE['secret_ref'], sot.secret_ref)
        self.assertEqual(EXAMPLE['status'], sot.status)
        self.assertEqual(EXAMPLE['type'], sot.type)
