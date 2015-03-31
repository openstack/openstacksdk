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

import mock
import testtools

from openstack.network.v2 import router

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'admin_state_up': True,
    'external_gateway_info': {'2': '3'},
    'id': IDENTIFIER,
    'name': '4',
    'tenant_id': '5',
    'status': '6',
}


class TestRouter(testtools.TestCase):

    def test_basic(self):
        sot = router.Router()
        self.assertEqual('router', sot.resource_key)
        self.assertEqual('routers', sot.resources_key)
        self.assertEqual('/routers', sot.base_path)
        self.assertEqual('network', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = router.Router(EXAMPLE)
        self.assertEqual(EXAMPLE['admin_state_up'], sot.admin_state_up)
        self.assertEqual(EXAMPLE['external_gateway_info'],
                         sot.external_gateway_info)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['tenant_id'], sot.project_id)
        self.assertEqual(EXAMPLE['status'], sot.status)

    def test_add_interface(self):
        sot = router.Router(EXAMPLE)
        response = mock.Mock()
        response.body = {"subnet_id": "3", "port_id": "2"}
        sess = mock.Mock()
        sess.put = mock.MagicMock()
        sess.put.return_value = response

        self.assertEqual(response.body, sot.add_interface(sess, '3'))

        url = 'routers/IDENTIFIER/add_router_interface'
        body = {"subnet_id": "3"}
        sess.put.assert_called_with(url, service=sot.service, json=body)

    def test_remove_interface(self):
        sot = router.Router(EXAMPLE)
        response = mock.Mock()
        response.body = {"subnet_id": "3", "port_id": "2"}
        sess = mock.Mock()
        sess.put = mock.MagicMock()
        sess.put.return_value = response

        self.assertEqual(response.body, sot.remove_interface(sess, '3'))

        url = 'routers/IDENTIFIER/remove_router_interface'
        body = {"subnet_id": "3"}
        sess.put.assert_called_with(url, service=sot.service, json=body)
