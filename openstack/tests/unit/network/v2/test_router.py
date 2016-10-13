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
    'availability_zone_hints': ['1'],
    'availability_zones': ['2'],
    'created_at': 'timestamp1',
    'description': '3',
    'distributed': False,
    'external_gateway_info': {'4': 4},
    'flavor_id': '5',
    'ha': False,
    'id': IDENTIFIER,
    'name': '6',
    'revision': 7,
    'routes': ['8'],
    'status': '9',
    'tenant_id': '10',
    'updated_at': 'timestamp2',
}

EXAMPLE_WITH_OPTIONAL = {
    'admin_state_up': False,
    'availability_zone_hints': ['zone-1', 'zone-2'],
    'availability_zones': ['zone-2'],
    'description': 'description',
    'distributed': True,
    'external_gateway_info': {
        'network_id': '1',
        'enable_snat': True,
        'external_fixed_ips': []
    },
    'ha': True,
    'id': IDENTIFIER,
    'name': 'router1',
    'routes': [{
        'nexthop': '172.24.4.20',
        'destination': '10.0.3.1/24'
    }],
    'status': 'ACTIVE',
    'tenant_id': '2',
}


class TestRouter(testtools.TestCase):

    def test_basic(self):
        sot = router.Router()
        self.assertEqual('router', sot.resource_key)
        self.assertEqual('routers', sot.resources_key)
        self.assertEqual('/routers', sot.base_path)
        self.assertEqual('network', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_get)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = router.Router(**EXAMPLE)
        self.assertTrue(sot.is_admin_state_up)
        self.assertEqual(EXAMPLE['availability_zone_hints'],
                         sot.availability_zone_hints)
        self.assertEqual(EXAMPLE['availability_zones'],
                         sot.availability_zones)
        self.assertEqual(EXAMPLE['created_at'], sot.created_at)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertFalse(sot.is_distributed)
        self.assertEqual(EXAMPLE['external_gateway_info'],
                         sot.external_gateway_info)
        self.assertEqual(EXAMPLE['flavor_id'], sot.flavor_id)
        self.assertFalse(sot.is_ha)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['revision'], sot.revision_number)
        self.assertEqual(EXAMPLE['routes'], sot.routes)
        self.assertEqual(EXAMPLE['status'], sot.status)
        self.assertEqual(EXAMPLE['tenant_id'], sot.project_id)
        self.assertEqual(EXAMPLE['updated_at'], sot.updated_at)

    def test_make_it_with_optional(self):
        sot = router.Router(**EXAMPLE_WITH_OPTIONAL)
        self.assertFalse(sot.is_admin_state_up)
        self.assertEqual(EXAMPLE_WITH_OPTIONAL['availability_zone_hints'],
                         sot.availability_zone_hints)
        self.assertEqual(EXAMPLE_WITH_OPTIONAL['availability_zones'],
                         sot.availability_zones)
        self.assertEqual(EXAMPLE_WITH_OPTIONAL['description'],
                         sot.description)
        self.assertTrue(sot.is_distributed)
        self.assertEqual(EXAMPLE_WITH_OPTIONAL['external_gateway_info'],
                         sot.external_gateway_info)
        self.assertTrue(sot.is_ha)
        self.assertEqual(EXAMPLE_WITH_OPTIONAL['id'], sot.id)
        self.assertEqual(EXAMPLE_WITH_OPTIONAL['name'], sot.name)
        self.assertEqual(EXAMPLE_WITH_OPTIONAL['routes'], sot.routes)
        self.assertEqual(EXAMPLE_WITH_OPTIONAL['status'], sot.status)
        self.assertEqual(EXAMPLE_WITH_OPTIONAL['tenant_id'], sot.project_id)

    def test_add_interface_subnet(self):
        # Add subnet to a router
        sot = router.Router(**EXAMPLE)
        response = mock.Mock()
        response.body = {"subnet_id": "3", "port_id": "2"}
        response.json = mock.Mock(return_value=response.body)
        sess = mock.Mock()
        sess.put = mock.Mock(return_value=response)
        body = {"subnet_id": "3"}
        self.assertEqual(response.body, sot.add_interface(sess, **body))

        url = 'routers/IDENTIFIER/add_router_interface'
        sess.put.assert_called_with(url, endpoint_filter=sot.service,
                                    json=body)

    def test_add_interface_port(self):
        # Add port to a router
        sot = router.Router(**EXAMPLE)
        response = mock.Mock()
        response.body = {"subnet_id": "3", "port_id": "3"}
        response.json = mock.Mock(return_value=response.body)
        sess = mock.Mock()
        sess.put = mock.Mock(return_value=response)

        body = {"port_id": "3"}
        self.assertEqual(response.body, sot.add_interface(sess, **body))

        url = 'routers/IDENTIFIER/add_router_interface'
        sess.put.assert_called_with(url, endpoint_filter=sot.service,
                                    json=body)

    def test_remove_interface_subnet(self):
        # Remove subnet from a router
        sot = router.Router(**EXAMPLE)
        response = mock.Mock()
        response.body = {"subnet_id": "3", "port_id": "2"}
        response.json = mock.Mock(return_value=response.body)
        sess = mock.Mock()
        sess.put = mock.Mock(return_value=response)
        body = {"subnet_id": "3"}
        self.assertEqual(response.body, sot.remove_interface(sess, **body))

        url = 'routers/IDENTIFIER/remove_router_interface'
        sess.put.assert_called_with(url, endpoint_filter=sot.service,
                                    json=body)

    def test_remove_interface_port(self):
        # Remove port from a router
        sot = router.Router(**EXAMPLE)
        response = mock.Mock()
        response.body = {"subnet_id": "3", "port_id": "3"}
        response.json = mock.Mock(return_value=response.body)
        sess = mock.Mock()
        sess.put = mock.Mock(return_value=response)
        body = {"network_id": 3, "enable_snat": True}
        self.assertEqual(response.body, sot.remove_interface(sess, **body))

        url = 'routers/IDENTIFIER/remove_router_interface'
        sess.put.assert_called_with(url, endpoint_filter=sot.service,
                                    json=body)

    def test_add_router_gateway(self):
        # Add gateway to a router
        sot = router.Router(**EXAMPLE_WITH_OPTIONAL)
        response = mock.Mock()
        response.body = {"network_id": "3", "enable_snat": True}
        response.json = mock.Mock(return_value=response.body)
        sess = mock.Mock()
        sess.put = mock.Mock(return_value=response)
        body = {"network_id": 3, "enable_snat": True}
        self.assertEqual(response.body, sot.add_gateway(sess, **body))

        url = 'routers/IDENTIFIER/add_gateway_router'
        sess.put.assert_called_with(url, endpoint_filter=sot.service,
                                    json=body)

    def test_remove_router_gateway(self):
        # Remove gateway to a router
        sot = router.Router(**EXAMPLE_WITH_OPTIONAL)
        response = mock.Mock()
        response.body = {"network_id": "3", "enable_snat": True}
        response.json = mock.Mock(return_value=response.body)
        sess = mock.Mock()
        sess.put = mock.Mock(return_value=response)
        body = {"network_id": 3, "enable_snat": True}
        self.assertEqual(response.body, sot.remove_gateway(sess, **body))

        url = 'routers/IDENTIFIER/remove_gateway_router'
        sess.put.assert_called_with(url, endpoint_filter=sot.service,
                                    json=body)


class TestL3AgentRouters(testtools.TestCase):

    def test_basic(self):
        sot = router.L3AgentRouter()
        self.assertEqual('router', sot.resource_key)
        self.assertEqual('routers', sot.resources_key)
        self.assertEqual('/agents/%(agent_id)s/l3-routers', sot.base_path)
        self.assertEqual('l3-router', sot.resource_name)
        self.assertEqual('network', sot.service.service_type)
        self.assertFalse(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertFalse(sot.allow_update)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)
