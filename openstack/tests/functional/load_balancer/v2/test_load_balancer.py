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

import unittest
import uuid

from openstack.load_balancer.v2 import listener
from openstack.load_balancer.v2 import load_balancer
from openstack.load_balancer.v2 import pool
from openstack.tests.functional import base
from openstack.tests.functional.load_balancer import base as lb_base


@unittest.skipUnless(base.service_exists(service_type='load-balancer'),
                     'Load-balancer service does not exist')
class TestLoadBalancer(lb_base.BaseLBFunctionalTest):

    LB_NAME = uuid.uuid4().hex
    LISTENER_NAME = uuid.uuid4().hex
    POOL_NAME = uuid.uuid4().hex
    UPDATE_NAME = uuid.uuid4().hex
    LB_ID = None
    LISTENER_ID = None
    POOL_ID = None
    VIP_SUBNET_ID = None
    PROJECT_ID = None
    PROTOCOL = 'HTTP'
    PROTOCOL_PORT = 80
    LB_ALGORITHM = 'ROUND_ROBIN'

    # Note: Creating load balancers can be slow on some hosts due to nova
    #       instance boot times (up to ten minutes) so we are consolidating
    #       all of our functional tests here to reduce test runtime.
    @classmethod
    def setUpClass(cls):
        super(TestLoadBalancer, cls).setUpClass()
        subnets = list(cls.conn.network.subnets())
        cls.VIP_SUBNET_ID = subnets[0].id
        cls.PROJECT_ID = cls.conn.session.get_project_id()
        test_lb = cls.conn.load_balancer.create_load_balancer(
            name=cls.LB_NAME, vip_subnet_id=cls.VIP_SUBNET_ID,
            project_id=cls.PROJECT_ID)
        assert isinstance(test_lb, load_balancer.LoadBalancer)
        cls.assertIs(cls.LB_NAME, test_lb.name)
        # Wait for the LB to go ACTIVE.  On non-virtualization enabled hosts
        # it can take nova up to ten minutes to boot a VM.
        cls.lb_wait_for_status(test_lb, status='ACTIVE',
                               failures=['ERROR'], interval=1, wait=600)
        cls.LB_ID = test_lb.id

        test_listener = cls.conn.load_balancer.create_listener(
            name=cls.LISTENER_NAME, protocol=cls.PROTOCOL,
            protocol_port=cls.PROTOCOL_PORT, loadbalancer_id=cls.LB_ID)
        assert isinstance(test_listener, listener.Listener)
        cls.assertIs(cls.LISTENER_NAME, test_listener.name)
        cls.LISTENER_ID = test_listener.id
        cls.lb_wait_for_status(test_lb, status='ACTIVE',
                               failures=['ERROR'])

        test_pool = cls.conn.load_balancer.create_pool(
            name=cls.POOL_NAME, protocol=cls.PROTOCOL,
            lb_algorithm=cls.LB_ALGORITHM, listener_id=cls.LISTENER_ID)
        assert isinstance(test_pool, pool.Pool)
        cls.assertIs(cls.POOL_NAME, test_pool.name)
        cls.POOL_ID = test_pool.id
        cls.lb_wait_for_status(test_lb, status='ACTIVE',
                               failures=['ERROR'])

    @classmethod
    def tearDownClass(cls):
        test_lb = cls.conn.load_balancer.get_load_balancer(cls.LB_ID)
        cls.lb_wait_for_status(test_lb, status='ACTIVE', failures=['ERROR'])

        cls.conn.load_balancer.delete_pool(cls.POOL_ID, ignore_missing=False)
        cls.lb_wait_for_status(test_lb, status='ACTIVE', failures=['ERROR'])

        cls.conn.load_balancer.delete_listener(cls.LISTENER_ID,
                                               ignore_missing=False)
        cls.lb_wait_for_status(test_lb, status='ACTIVE', failures=['ERROR'])

        cls.conn.load_balancer.delete_load_balancer(
            cls.LB_ID, ignore_missing=False)

    def test_lb_find(self):
        test_lb = self.conn.load_balancer.find_load_balancer(self.LB_NAME)
        self.assertEqual(self.LB_ID, test_lb.id)

    def test_lb_get(self):
        test_lb = self.conn.load_balancer.get_load_balancer(self.LB_ID)
        self.assertEqual(self.LB_NAME, test_lb.name)
        self.assertEqual(self.LB_ID, test_lb.id)
        self.assertEqual(self.VIP_SUBNET_ID, test_lb.vip_subnet_id)

    def test_lb_list(self):
        names = [lb.name for lb in self.conn.load_balancer.load_balancers()]
        self.assertIn(self.LB_NAME, names)

    def test_lb_update(self):
        update_lb = self.conn.load_balancer.update_load_balancer(
            self.LB_ID, name=self.UPDATE_NAME)
        self.lb_wait_for_status(update_lb, status='ACTIVE',
                                failures=['ERROR'])
        test_lb = self.conn.load_balancer.get_load_balancer(self.LB_ID)
        self.assertEqual(self.UPDATE_NAME, test_lb.name)

        update_lb = self.conn.load_balancer.update_load_balancer(
            self.LB_ID, name=self.LB_NAME)
        self.lb_wait_for_status(update_lb, status='ACTIVE',
                                failures=['ERROR'])
        test_lb = self.conn.load_balancer.get_load_balancer(self.LB_ID)
        self.assertEqual(self.LB_NAME, test_lb.name)

    def test_listener_find(self):
        test_listener = self.conn.load_balancer.find_listener(
            self.LISTENER_NAME)
        self.assertEqual(self.LISTENER_ID, test_listener.id)

    def test_listener_get(self):
        test_listener = self.conn.load_balancer.get_listener(self.LISTENER_ID)
        self.assertEqual(self.LISTENER_NAME, test_listener.name)
        self.assertEqual(self.LISTENER_ID, test_listener.id)
        self.assertEqual(self.PROTOCOL, test_listener.protocol)
        self.assertEqual(self.PROTOCOL_PORT, test_listener.protocol_port)

    def test_listener_list(self):
        names = [ls.name for ls in self.conn.load_balancer.listeners()]
        self.assertIn(self.LISTENER_NAME, names)

    def test_listener_update(self):
        test_lb = self.conn.load_balancer.get_load_balancer(self.LB_ID)

        self.conn.load_balancer.update_listener(
            self.LISTENER_ID, name=self.UPDATE_NAME)
        self.lb_wait_for_status(test_lb, status='ACTIVE',
                                failures=['ERROR'])
        test_listener = self.conn.load_balancer.get_listener(self.LISTENER_ID)
        self.assertEqual(self.UPDATE_NAME, test_listener.name)

        self.conn.load_balancer.update_listener(
            self.LISTENER_ID, name=self.LISTENER_NAME)
        self.lb_wait_for_status(test_lb, status='ACTIVE',
                                failures=['ERROR'])
        test_listener = self.conn.load_balancer.get_listener(self.LISTENER_ID)
        self.assertEqual(self.LISTENER_NAME, test_listener.name)

    def test_pool_find(self):
        test_pool = self.conn.load_balancer.find_pool(self.POOL_NAME)
        self.assertEqual(self.POOL_ID, test_pool.id)

    def test_pool_get(self):
        test_pool = self.conn.load_balancer.get_pool(self.POOL_ID)
        self.assertEqual(self.POOL_NAME, test_pool.name)
        self.assertEqual(self.POOL_ID, test_pool.id)
        self.assertEqual(self.PROTOCOL, test_pool.protocol)

    def test_pool_list(self):
        names = [pool.name for pool in self.conn.load_balancer.pools()]
        self.assertIn(self.POOL_NAME, names)

    def test_pool_update(self):
        test_lb = self.conn.load_balancer.get_load_balancer(self.LB_ID)

        self.conn.load_balancer.update_pool(self.POOL_ID,
                                            name=self.UPDATE_NAME)
        self.lb_wait_for_status(test_lb, status='ACTIVE', failures=['ERROR'])
        test_pool = self.conn.load_balancer.get_pool(self.POOL_ID)
        self.assertEqual(self.UPDATE_NAME, test_pool.name)

        self.conn.load_balancer.update_pool(self.POOL_ID,
                                            name=self.POOL_NAME)
        self.lb_wait_for_status(test_lb, status='ACTIVE', failures=['ERROR'])
        test_pool = self.conn.load_balancer.get_pool(self.POOL_ID)
        self.assertEqual(self.POOL_NAME, test_pool.name)
