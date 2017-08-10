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

from openstack.load_balancer.v2 import load_balancer
from openstack.tests.functional import base
from openstack.tests.functional.load_balancer import base as lb_base


@unittest.skipUnless(base.service_exists(service_type='load-balancer'),
                     'Load-balancer service does not exist')
class TestLoadBalancer(lb_base.BaseLBFunctionalTest):

    NAME = uuid.uuid4().hex
    ID = None
    VIP_SUBNET_ID = None
    PROJECT_ID = None
    UPDATE_NAME = uuid.uuid4().hex

    @classmethod
    def setUpClass(cls):
        super(TestLoadBalancer, cls).setUpClass()
        subnets = list(cls.conn.network.subnets())
        cls.VIP_SUBNET_ID = subnets[0].id
        cls.PROJECT_ID = cls.conn.session.get_project_id()
        test_lb = cls.conn.load_balancer.create_load_balancer(
            name=cls.NAME, vip_subnet_id=cls.VIP_SUBNET_ID,
            project_id=cls.PROJECT_ID)
        assert isinstance(test_lb, load_balancer.LoadBalancer)
        cls.assertIs(cls.NAME, test_lb.name)
        # Wait for the LB to go ACTIVE.  On non-virtualization enabled hosts
        # it can take nova up to ten minutes to boot a VM.
        cls.lb_wait_for_status(test_lb, status='ACTIVE',
                               failures=['ERROR'], interval=1, wait=600)
        cls.ID = test_lb.id

    @classmethod
    def tearDownClass(cls):
        test_lb = cls.conn.load_balancer.get_load_balancer(cls.ID)
        cls.lb_wait_for_status(test_lb, status='ACTIVE',
                               failures=['ERROR'])
        cls.conn.load_balancer.delete_load_balancer(
            cls.ID, ignore_missing=False)

    def test_find(self):
        test_lb = self.conn.load_balancer.find_load_balancer(self.NAME)
        self.assertEqual(self.ID, test_lb.id)

    def test_get(self):
        test_lb = self.conn.load_balancer.get_load_balancer(self.ID)
        self.assertEqual(self.NAME, test_lb.name)
        self.assertEqual(self.ID, test_lb.id)
        self.assertEqual(self.VIP_SUBNET_ID, test_lb.vip_subnet_id)

    def test_list(self):
        names = [lb.name for lb in self.conn.load_balancer.load_balancers()]
        self.assertIn(self.NAME, names)

    def test_update(self):
        update_lb = self.conn.load_balancer.update_load_balancer(
            self.ID, name=self.UPDATE_NAME)
        self.lb_wait_for_status(update_lb, status='ACTIVE',
                                failures=['ERROR'])
        test_lb = self.conn.load_balancer.get_load_balancer(self.ID)
        self.assertEqual(self.UPDATE_NAME, test_lb.name)
