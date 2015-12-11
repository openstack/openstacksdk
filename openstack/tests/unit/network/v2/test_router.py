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
    'routes': [],
}

EXAMPLE_WITH_OPTIONAL = {
    'admin_state_up': False,
    'external_gateway_info': {'network_id': '1',
                              'enable_snat': True,
                              'external_fixed_ips': []},
    'id': IDENTIFIER,
    'name': 'router1',
    'tenant_id': '2',
    'status': 'ACTIVE',
    'routes': [{'nexthop': '172.24.4.20', 'destination': '10.0.3.1/24'}],
    'ha': True,
    'distributed': True,
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
        self.assertFalse(sot.is_ha)
        self.assertFalse(sot.is_distributed)
        self.assertEqual(EXAMPLE['routes'], sot.routes)

    def test_make_it_with_optional(self):
        sot = router.Router(EXAMPLE_WITH_OPTIONAL)
        self.assertEqual(EXAMPLE_WITH_OPTIONAL['admin_state_up'],
                         sot.admin_state_up)
        self.assertEqual(EXAMPLE_WITH_OPTIONAL['external_gateway_info'],
                         sot.external_gateway_info)
        self.assertEqual(EXAMPLE_WITH_OPTIONAL['id'], sot.id)
        self.assertEqual(EXAMPLE_WITH_OPTIONAL['name'], sot.name)
        self.assertEqual(EXAMPLE_WITH_OPTIONAL['tenant_id'], sot.project_id)
        self.assertEqual(EXAMPLE_WITH_OPTIONAL['status'], sot.status)
        self.assertEqual(EXAMPLE_WITH_OPTIONAL['ha'], sot.is_ha)
        self.assertEqual(EXAMPLE_WITH_OPTIONAL['distributed'],
                         sot.is_distributed)
        self.assertEqual(EXAMPLE_WITH_OPTIONAL['routes'], sot.routes)

    def test_add_interface(self):
        sot = router.Router(EXAMPLE)
        response = mock.Mock()
        response.body = {"subnet_id": "3", "port_id": "2"}
        response.json = mock.Mock(return_value=response.body)
        sess = mock.Mock()
        sess.put = mock.Mock(return_value=response)

        self.assertEqual(response.body, sot.add_interface(sess, '3'))

        url = 'routers/IDENTIFIER/add_router_interface'
        body = {"subnet_id": "3"}
        sess.put.assert_called_with(url, endpoint_filter=sot.service,
                                    json=body)

    def test_remove_interface(self):
        sot = router.Router(EXAMPLE)
        response = mock.Mock()
        response.body = {"subnet_id": "3", "port_id": "2"}
        response.json = mock.Mock(return_value=response.body)
        sess = mock.Mock()
        sess.put = mock.Mock(return_value=response)

        self.assertEqual(response.body, sot.remove_interface(sess, '3'))

        url = 'routers/IDENTIFIER/remove_router_interface'
        body = {"subnet_id": "3"}
        sess.put.assert_called_with(url, endpoint_filter=sot.service,
                                    json=body)
