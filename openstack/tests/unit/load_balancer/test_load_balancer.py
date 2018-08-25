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
from openstack.tests.unit import base
import uuid

from openstack.load_balancer.v2 import load_balancer

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'admin_state_up': True,
    'created_at': '2017-07-17T12:14:57.233772',
    'description': 'fake_description',
    'flavor': uuid.uuid4(),
    'id': IDENTIFIER,
    'listeners': [{'id', uuid.uuid4()}],
    'name': 'test_load_balancer',
    'operating_status': 'ONLINE',
    'pools': [{'id', uuid.uuid4()}],
    'project_id': uuid.uuid4(),
    'provider': 'fake_provider',
    'provisioning_status': 'ACTIVE',
    'updated_at': '2017-07-17T12:16:57.233772',
    'vip_address': '192.0.2.5',
    'vip_network_id': uuid.uuid4(),
    'vip_port_id': uuid.uuid4(),
    'vip_subnet_id': uuid.uuid4(),
    'vip_qos_policy_id': uuid.uuid4(),
}


class TestLoadBalancer(base.TestCase):

    def test_basic(self):
        test_load_balancer = load_balancer.LoadBalancer()
        self.assertEqual('loadbalancer', test_load_balancer.resource_key)
        self.assertEqual('loadbalancers', test_load_balancer.resources_key)
        self.assertEqual('/lbaas/loadbalancers',
                         test_load_balancer.base_path)
        self.assertTrue(test_load_balancer.allow_create)
        self.assertTrue(test_load_balancer.allow_fetch)
        self.assertTrue(test_load_balancer.allow_delete)
        self.assertTrue(test_load_balancer.allow_list)
        self.assertTrue(test_load_balancer.allow_commit)

    def test_make_it(self):
        test_load_balancer = load_balancer.LoadBalancer(**EXAMPLE)
        self.assertTrue(test_load_balancer.is_admin_state_up)
        self.assertEqual(EXAMPLE['created_at'], test_load_balancer.created_at),
        self.assertEqual(EXAMPLE['description'],
                         test_load_balancer.description)
        self.assertEqual(EXAMPLE['flavor'], test_load_balancer.flavor)
        self.assertEqual(EXAMPLE['id'], test_load_balancer.id)
        self.assertEqual(EXAMPLE['listeners'], test_load_balancer.listeners)
        self.assertEqual(EXAMPLE['name'], test_load_balancer.name)
        self.assertEqual(EXAMPLE['operating_status'],
                         test_load_balancer.operating_status)
        self.assertEqual(EXAMPLE['pools'], test_load_balancer.pools)
        self.assertEqual(EXAMPLE['project_id'], test_load_balancer.project_id)
        self.assertEqual(EXAMPLE['provider'], test_load_balancer.provider)
        self.assertEqual(EXAMPLE['provisioning_status'],
                         test_load_balancer.provisioning_status)
        self.assertEqual(EXAMPLE['updated_at'], test_load_balancer.updated_at),
        self.assertEqual(EXAMPLE['vip_address'],
                         test_load_balancer.vip_address)
        self.assertEqual(EXAMPLE['vip_network_id'],
                         test_load_balancer.vip_network_id)
        self.assertEqual(EXAMPLE['vip_port_id'],
                         test_load_balancer.vip_port_id)
        self.assertEqual(EXAMPLE['vip_subnet_id'],
                         test_load_balancer.vip_subnet_id)
        self.assertEqual(EXAMPLE['vip_qos_policy_id'],
                         test_load_balancer.vip_qos_policy_id)

    def test_delete_non_cascade(self):
        sess = mock.Mock()
        resp = mock.Mock()
        sess.delete.return_value = resp

        sot = load_balancer.LoadBalancer(**EXAMPLE)
        sot.cascade = False
        sot._translate_response = mock.Mock()
        sot.delete(sess)

        url = 'lbaas/loadbalancers/%(lb)s' % {
            'lb': EXAMPLE['id']
        }
        headers = {'Accept': ''}
        params = {}
        sess.delete.assert_called_with(url,
                                       headers=headers,
                                       params=params)
        sot._translate_response.assert_called_once_with(
            resp,
            error_message=None,
            has_body=False,
        )

    def test_delete_cascade(self):
        sess = mock.Mock()
        resp = mock.Mock()
        sess.delete.return_value = resp

        sot = load_balancer.LoadBalancer(**EXAMPLE)
        sot.cascade = True
        sot._translate_response = mock.Mock()
        sot.delete(sess)

        url = 'lbaas/loadbalancers/%(lb)s' % {
            'lb': EXAMPLE['id']
        }
        headers = {'Accept': ''}
        params = {'cascade': True}
        sess.delete.assert_called_with(url,
                                       headers=headers,
                                       params=params)
        sot._translate_response.assert_called_once_with(
            resp,
            error_message=None,
            has_body=False,
        )
