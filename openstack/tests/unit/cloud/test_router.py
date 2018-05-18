# Copyright 2017 OVH SAS
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import copy
import testtools

from openstack.cloud import exc
from openstack.tests.unit import base


class TestRouter(base.TestCase):

    router_name = 'goofy'
    router_id = '57076620-dcfb-42ed-8ad6-79ccb4a79ed2'
    subnet_id = '1f1696eb-7f47-47f6-835c-4889bff88604'

    mock_router_rep = {
        'admin_state_up': True,
        'availability_zone_hints': [],
        'availability_zones': [],
        'description': u'',
        'distributed': False,
        'external_gateway_info': None,
        'flavor_id': None,
        'ha': False,
        'id': router_id,
        'name': router_name,
        'project_id': u'861808a93da0484ea1767967c4df8a23',
        'routes': [],
        'status': u'ACTIVE',
        'tenant_id': u'861808a93da0484ea1767967c4df8a23'
    }

    mock_router_interface_rep = {
        'network_id': '53aee281-b06d-47fc-9e1a-37f045182b8e',
        'subnet_id': '1f1696eb-7f47-47f6-835c-4889bff88604',
        'tenant_id': '861808a93da0484ea1767967c4df8a23',
        'subnet_ids': [subnet_id],
        'port_id': '23999891-78b3-4a6b-818d-d1b713f67848',
        'id': '57076620-dcfb-42ed-8ad6-79ccb4a79ed2',
        'request_ids': ['req-f1b0b1b4-ae51-4ef9-b371-0cc3c3402cf7']
    }

    router_availability_zone_extension = {
        "alias": "router_availability_zone",
        "updated": "2015-01-01T10:00:00-00:00",
        "description": "Availability zone support for router.",
        "links": [],
        "name": "Router Availability Zone"
    }

    enabled_neutron_extensions = [router_availability_zone_extension]

    def test_get_router(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'routers.json']),
                 json={'routers': [self.mock_router_rep]})
        ])
        r = self.cloud.get_router(self.router_name)
        self.assertIsNotNone(r)
        self.assertDictEqual(self.mock_router_rep, r)
        self.assert_calls()

    def test_get_router_not_found(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'routers.json']),
                 json={'routers': []})
        ])
        r = self.cloud.get_router('mickey')
        self.assertIsNone(r)
        self.assert_calls()

    def test_create_router(self):
        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'routers.json']),
                 json={'router': self.mock_router_rep},
                 validate=dict(
                     json={'router': {
                         'name': self.router_name,
                         'admin_state_up': True}}))
        ])
        new_router = self.cloud.create_router(name=self.router_name,
                                              admin_state_up=True)
        self.assertDictEqual(self.mock_router_rep, new_router)
        self.assert_calls()

    def test_create_router_specific_tenant(self):
        new_router_tenant_id = "project_id_value"
        mock_router_rep = copy.copy(self.mock_router_rep)
        mock_router_rep['tenant_id'] = new_router_tenant_id
        mock_router_rep['project_id'] = new_router_tenant_id
        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'routers.json']),
                 json={'router': mock_router_rep},
                 validate=dict(
                     json={'router': {
                         'name': self.router_name,
                         'admin_state_up': True,
                         'tenant_id': new_router_tenant_id}}))
        ])

        self.cloud.create_router(self.router_name,
                                 project_id=new_router_tenant_id)
        self.assert_calls()

    def test_create_router_with_availability_zone_hints(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 json={'extensions': self.enabled_neutron_extensions}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'routers.json']),
                 json={'router': self.mock_router_rep},
                 validate=dict(
                     json={'router': {
                         'name': self.router_name,
                         'admin_state_up': True,
                         'availability_zone_hints': ['nova']}}))
        ])
        self.cloud.create_router(
            name=self.router_name, admin_state_up=True,
            availability_zone_hints=['nova'])
        self.assert_calls()

    def test_create_router_without_enable_snat(self):
        """Do not send enable_snat when not given."""
        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'routers.json']),
                 json={'router': self.mock_router_rep},
                 validate=dict(
                     json={'router': {
                         'name': self.router_name,
                         'admin_state_up': True}}))
        ])
        self.cloud.create_router(
            name=self.router_name, admin_state_up=True)
        self.assert_calls()

    def test_create_router_with_enable_snat_True(self):
        """Send enable_snat when it is True."""
        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'routers.json']),
                 json={'router': self.mock_router_rep},
                 validate=dict(
                     json={'router': {
                         'name': self.router_name,
                         'admin_state_up': True,
                         'external_gateway_info': {'enable_snat': True}}}))
        ])
        self.cloud.create_router(
            name=self.router_name, admin_state_up=True, enable_snat=True)
        self.assert_calls()

    def test_create_router_with_enable_snat_False(self):
        """Send enable_snat when it is False."""
        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'routers.json']),
                 json={'router': self.mock_router_rep},
                 validate=dict(
                     json={'router': {
                         'name': self.router_name,
                         'external_gateway_info': {'enable_snat': False},
                         'admin_state_up': True}}))
        ])
        self.cloud.create_router(
            name=self.router_name, admin_state_up=True, enable_snat=False)
        self.assert_calls()

    def test_create_router_wrong_availability_zone_hints_type(self):
        azh_opts = "invalid"
        with testtools.ExpectedException(
            exc.OpenStackCloudException,
            "Parameter 'availability_zone_hints' must be a list"
        ):
            self.cloud.create_router(
                name=self.router_name, admin_state_up=True,
                availability_zone_hints=azh_opts)

    def test_add_router_interface(self):
        self.register_uris([
            dict(method='PUT',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'routers', self.router_id,
                             'add_router_interface.json']),
                 json={'port': self.mock_router_interface_rep},
                 validate=dict(
                     json={'subnet_id': self.subnet_id}))
        ])
        self.cloud.add_router_interface(
            {'id': self.router_id}, subnet_id=self.subnet_id)
        self.assert_calls()

    def test_remove_router_interface(self):
        self.register_uris([
            dict(method='PUT',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'routers', self.router_id,
                             'remove_router_interface.json']),
                 json={'port': self.mock_router_interface_rep},
                 validate=dict(
                     json={'subnet_id': self.subnet_id}))
        ])
        self.cloud.remove_router_interface(
            {'id': self.router_id}, subnet_id=self.subnet_id)
        self.assert_calls()

    def test_remove_router_interface_missing_argument(self):
        self.assertRaises(ValueError, self.cloud.remove_router_interface,
                          {'id': '123'})

    def test_update_router(self):
        new_router_name = "mickey"
        expected_router_rep = copy.copy(self.mock_router_rep)
        expected_router_rep['name'] = new_router_name
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'routers.json']),
                 json={'routers': [self.mock_router_rep]}),
            dict(method='PUT',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'routers', '%s.json' % self.router_id]),
                 json={'router': expected_router_rep},
                 validate=dict(
                     json={'router': {
                         'name': new_router_name}}))
        ])
        new_router = self.cloud.update_router(
            self.router_id, name=new_router_name)
        self.assertDictEqual(expected_router_rep, new_router)
        self.assert_calls()

    def test_delete_router(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'routers.json']),
                 json={'routers': [self.mock_router_rep]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'routers', '%s.json' % self.router_id]),
                 json={})
        ])
        self.assertTrue(self.cloud.delete_router(self.router_name))
        self.assert_calls()

    def test_delete_router_not_found(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'routers.json']),
                 json={'routers': []}),
        ])
        self.assertFalse(self.cloud.delete_router(self.router_name))
        self.assert_calls()

    def test_delete_router_multiple_found(self):
        router1 = dict(id='123', name='mickey')
        router2 = dict(id='456', name='mickey')
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'routers.json']),
                 json={'routers': [router1, router2]}),
        ])
        self.assertRaises(exc.OpenStackCloudException,
                          self.cloud.delete_router,
                          'mickey')
        self.assert_calls()

    def test_delete_router_multiple_using_id(self):
        router1 = dict(id='123', name='mickey')
        router2 = dict(id='456', name='mickey')
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'routers.json']),
                 json={'routers': [router1, router2]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'routers', '123.json']),
                 json={})
        ])
        self.assertTrue(self.cloud.delete_router("123"))
        self.assert_calls()

    def _get_mock_dict(self, owner, json):
        return dict(method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'ports.json'],
                        qs_elements=["device_id=%s" % self.router_id,
                                     "device_owner=network:%s" % owner]),
                    json=json)

    def _test_list_router_interfaces(self, router, interface_type,
                                     router_type="normal",
                                     expected_result=None):
        if router_type == "normal":
            device_owner = 'router_interface'
        elif router_type == "ha":
            device_owner = 'ha_router_replicated_interface'
        elif router_type == "dvr":
            device_owner = 'router_interface_distributed'
        internal_port = {
            'id': 'internal_port_id',
            'fixed_ips': [{
                'subnet_id': 'internal_subnet_id',
                'ip_address': "10.0.0.1"
            }],
            'device_id': self.router_id,
            'device_owner': 'network:%s' % device_owner
        }
        external_port = {
            'id': 'external_port_id',
            'fixed_ips': [{
                'subnet_id': 'external_subnet_id',
                'ip_address': "1.2.3.4"
            }],
            'device_id': self.router_id,
            'device_owner': 'network:router_gateway'
        }
        if expected_result is None:
            if interface_type == "internal":
                expected_result = [internal_port]
            elif interface_type == "external":
                expected_result = [external_port]
            else:
                expected_result = [internal_port, external_port]

        mock_uris = []
        for port_type in ['router_interface',
                          'router_interface_distributed',
                          'ha_router_replicated_interface']:
            ports = {}
            if port_type == device_owner:
                ports = {'ports': [internal_port]}
            mock_uris.append(self._get_mock_dict(port_type, ports))
        mock_uris.append(self._get_mock_dict('router_gateway',
                                             {'ports': [external_port]}))

        self.register_uris(mock_uris)
        ret = self.cloud.list_router_interfaces(router, interface_type)
        self.assertEqual(expected_result, ret)
        self.assert_calls()

    router = {
        'id': router_id,
        'external_gateway_info': {
            'external_fixed_ips': [{
                'subnet_id': 'external_subnet_id',
                'ip_address': '1.2.3.4'}]
        }
    }

    def test_list_router_interfaces_all(self):
        self._test_list_router_interfaces(self.router,
                                          interface_type=None)

    def test_list_router_interfaces_internal(self):
        self._test_list_router_interfaces(self.router,
                                          interface_type="internal")

    def test_list_router_interfaces_external(self):
        self._test_list_router_interfaces(self.router,
                                          interface_type="external")

    def test_list_router_interfaces_internal_ha(self):
        self._test_list_router_interfaces(self.router, router_type="ha",
                                          interface_type="internal")

    def test_list_router_interfaces_internal_dvr(self):
        self._test_list_router_interfaces(self.router, router_type="dvr",
                                          interface_type="internal")
