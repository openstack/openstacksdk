# Copyright 2019 Rackspace, US Inc.
#
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
import uuid

from openstack.load_balancer.v2 import amphora

IDENTIFIER = uuid.uuid4()
LB_ID = uuid.uuid4()
LISTENER_ID = uuid.uuid4()
COMPUTE_ID = uuid.uuid4()
VRRP_PORT_ID = uuid.uuid4()
HA_PORT_ID = uuid.uuid4()
IMAGE_ID = uuid.uuid4()
COMPUTE_FLAVOR = uuid.uuid4()
AMPHORA_ID = uuid.uuid4()

EXAMPLE = {
    'id': IDENTIFIER,
    'loadbalancer_id': LB_ID,
    'compute_id': COMPUTE_ID,
    'lb_network_ip': '192.168.1.2',
    'vrrp_ip': '192.168.1.5',
    'ha_ip': '192.168.1.10',
    'vrrp_port_id': VRRP_PORT_ID,
    'ha_port_id': HA_PORT_ID,
    'cert_expiration': '2019-09-19 00:34:51',
    'cert_busy': 0,
    'role': 'MASTER',
    'status': 'ALLOCATED',
    'vrrp_interface': 'eth1',
    'vrrp_id': 1,
    'vrrp_priority': 100,
    'cached_zone': 'zone1',
    'created_at': '2017-05-10T18:14:44',
    'updated_at': '2017-05-10T23:08:12',
    'image_id': IMAGE_ID,
    'compute_flavor': COMPUTE_FLAVOR
}


class TestAmphora(base.TestCase):

    def test_basic(self):
        test_amphora = amphora.Amphora()
        self.assertEqual('amphora', test_amphora.resource_key)
        self.assertEqual('amphorae', test_amphora.resources_key)
        self.assertEqual('/octavia/amphorae', test_amphora.base_path)
        self.assertFalse(test_amphora.allow_create)
        self.assertTrue(test_amphora.allow_fetch)
        self.assertFalse(test_amphora.allow_commit)
        self.assertFalse(test_amphora.allow_delete)
        self.assertTrue(test_amphora.allow_list)

    def test_make_it(self):
        test_amphora = amphora.Amphora(**EXAMPLE)
        self.assertEqual(IDENTIFIER, test_amphora.id)
        self.assertEqual(LB_ID, test_amphora.loadbalancer_id)
        self.assertEqual(COMPUTE_ID, test_amphora.compute_id)
        self.assertEqual(EXAMPLE['lb_network_ip'], test_amphora.lb_network_ip)
        self.assertEqual(EXAMPLE['vrrp_ip'], test_amphora.vrrp_ip)
        self.assertEqual(EXAMPLE['ha_ip'], test_amphora.ha_ip)
        self.assertEqual(VRRP_PORT_ID, test_amphora.vrrp_port_id)
        self.assertEqual(HA_PORT_ID, test_amphora.ha_port_id)
        self.assertEqual(EXAMPLE['cert_expiration'],
                         test_amphora.cert_expiration)
        self.assertEqual(EXAMPLE['cert_busy'], test_amphora.cert_busy)
        self.assertEqual(EXAMPLE['role'], test_amphora.role)
        self.assertEqual(EXAMPLE['status'], test_amphora.status)
        self.assertEqual(EXAMPLE['vrrp_interface'],
                         test_amphora.vrrp_interface)
        self.assertEqual(EXAMPLE['vrrp_id'], test_amphora.vrrp_id)
        self.assertEqual(EXAMPLE['vrrp_priority'], test_amphora.vrrp_priority)
        self.assertEqual(EXAMPLE['cached_zone'], test_amphora.cached_zone)
        self.assertEqual(EXAMPLE['created_at'], test_amphora.created_at)
        self.assertEqual(EXAMPLE['updated_at'], test_amphora.updated_at)
        self.assertEqual(IMAGE_ID, test_amphora.image_id)
        self.assertEqual(COMPUTE_FLAVOR, test_amphora.compute_flavor)

        self.assertDictEqual(
            {'limit': 'limit',
             'marker': 'marker',
             'id': 'id',
             'loadbalancer_id': 'loadbalancer_id',
             'compute_id': 'compute_id',
             'lb_network_ip': 'lb_network_ip',
             'vrrp_ip': 'vrrp_ip',
             'ha_ip': 'ha_ip',
             'vrrp_port_id': 'vrrp_port_id',
             'ha_port_id': 'ha_port_id',
             'cert_expiration': 'cert_expiration',
             'cert_busy': 'cert_busy',
             'role': 'role',
             'status': 'status',
             'vrrp_interface': 'vrrp_interface',
             'vrrp_id': 'vrrp_id',
             'vrrp_priority': 'vrrp_priority',
             'cached_zone': 'cached_zone',
             'created_at': 'created_at',
             'updated_at': 'updated_at',
             'image_id': 'image_id',
             'image_id': 'image_id'
             },
            test_amphora._query_mapping._mapping)


class TestAmphoraConfig(base.TestCase):

    def test_basic(self):
        test_amp_config = amphora.AmphoraConfig()
        self.assertEqual('/octavia/amphorae/%(amphora_id)s/config',
                         test_amp_config.base_path)
        self.assertFalse(test_amp_config.allow_create)
        self.assertFalse(test_amp_config.allow_fetch)
        self.assertTrue(test_amp_config.allow_commit)
        self.assertFalse(test_amp_config.allow_delete)
        self.assertFalse(test_amp_config.allow_list)


class TestAmphoraFailover(base.TestCase):

    def test_basic(self):
        test_amp_failover = amphora.AmphoraFailover()
        self.assertEqual('/octavia/amphorae/%(amphora_id)s/failover',
                         test_amp_failover.base_path)
        self.assertFalse(test_amp_failover.allow_create)
        self.assertFalse(test_amp_failover.allow_fetch)
        self.assertTrue(test_amp_failover.allow_commit)
        self.assertFalse(test_amp_failover.allow_delete)
        self.assertFalse(test_amp_failover.allow_list)
