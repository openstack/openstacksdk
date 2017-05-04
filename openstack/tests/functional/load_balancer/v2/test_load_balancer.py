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


@unittest.skipUnless(base.service_exists(service_type='load_balancer'),
                     'Load-balancing service does not exist')
class TestLoadBalancer(base.BaseFunctionalTest):

    NAME = uuid.uuid4().hex
    ID = None
    VIP_SUBNET_ID = uuid.uuid4().hex

    @classmethod
    def setUpClass(cls):
        super(TestLoadBalancer, cls).setUpClass()
        test_lb = cls.conn.load_balancer.create_load_balancer(
            name=cls.NAME, vip_subnet_id=cls.VIP_SUBNET_ID)
        assert isinstance(test_lb, load_balancer.LoadBalancer)
        cls.assertIs(cls.NAME, test_lb.name)
        cls.ID = test_lb.id

    @classmethod
    def tearDownClass(cls):
        test_lb = cls.conn.load_balancer.delete_load_balancer(
            cls.ID, ignore_missing=False)
        cls.assertIs(None, test_lb)

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
