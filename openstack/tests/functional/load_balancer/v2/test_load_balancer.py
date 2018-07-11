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

from openstack.load_balancer.v2 import health_monitor
from openstack.load_balancer.v2 import l7_policy
from openstack.load_balancer.v2 import l7_rule
from openstack.load_balancer.v2 import listener
from openstack.load_balancer.v2 import load_balancer
from openstack.load_balancer.v2 import member
from openstack.load_balancer.v2 import pool
from openstack.tests.functional import base


class TestLoadBalancer(base.BaseFunctionalTest):

    HM_ID = None
    L7POLICY_ID = None
    LB_ID = None
    LISTENER_ID = None
    MEMBER_ID = None
    POOL_ID = None
    VIP_SUBNET_ID = None
    PROJECT_ID = None
    PROTOCOL = 'HTTP'
    PROTOCOL_PORT = 80
    LB_ALGORITHM = 'ROUND_ROBIN'
    MEMBER_ADDRESS = '192.0.2.16'
    WEIGHT = 10
    DELAY = 2
    TIMEOUT = 1
    MAX_RETRY = 3
    HM_TYPE = 'HTTP'
    ACTION = 'REDIRECT_TO_URL'
    REDIRECT_URL = 'http://www.example.com'
    COMPARE_TYPE = 'CONTAINS'
    L7RULE_TYPE = 'HOST_NAME'
    L7RULE_VALUE = 'example'

    # TODO(shade): Creating load balancers can be slow on some hosts due to
    #              nova instance boot times (up to ten minutes). This used to
    #              use setUpClass, but that's a whole other pile of bad, so
    #              we may need to engineer something pleasing here.
    def setUp(self):
        super(TestLoadBalancer, self).setUp()
        self.require_service('load-balancer')

        self.HM_NAME = self.getUniqueString()
        self.L7POLICY_NAME = self.getUniqueString()
        self.LB_NAME = self.getUniqueString()
        self.LISTENER_NAME = self.getUniqueString()
        self.MEMBER_NAME = self.getUniqueString()
        self.POOL_NAME = self.getUniqueString()
        self.UPDATE_NAME = self.getUniqueString()
        subnets = list(self.conn.network.subnets())
        self.VIP_SUBNET_ID = subnets[0].id
        self.PROJECT_ID = self.conn.session.get_project_id()
        test_lb = self.conn.load_balancer.create_load_balancer(
            name=self.LB_NAME, vip_subnet_id=self.VIP_SUBNET_ID,
            project_id=self.PROJECT_ID)
        assert isinstance(test_lb, load_balancer.LoadBalancer)
        self.assertEqual(self.LB_NAME, test_lb.name)
        # Wait for the LB to go ACTIVE.  On non-virtualization enabled hosts
        # it can take nova up to ten minutes to boot a VM.
        self.conn.load_balancer.wait_for_load_balancer(test_lb.id, interval=1,
                                                       wait=600)
        self.LB_ID = test_lb.id

        test_listener = self.conn.load_balancer.create_listener(
            name=self.LISTENER_NAME, protocol=self.PROTOCOL,
            protocol_port=self.PROTOCOL_PORT, loadbalancer_id=self.LB_ID)
        assert isinstance(test_listener, listener.Listener)
        self.assertEqual(self.LISTENER_NAME, test_listener.name)
        self.LISTENER_ID = test_listener.id
        self.conn.load_balancer.wait_for_load_balancer(self.LB_ID)

        test_pool = self.conn.load_balancer.create_pool(
            name=self.POOL_NAME, protocol=self.PROTOCOL,
            lb_algorithm=self.LB_ALGORITHM, listener_id=self.LISTENER_ID)
        assert isinstance(test_pool, pool.Pool)
        self.assertEqual(self.POOL_NAME, test_pool.name)
        self.POOL_ID = test_pool.id
        self.conn.load_balancer.wait_for_load_balancer(self.LB_ID)

        test_member = self.conn.load_balancer.create_member(
            pool=self.POOL_ID, name=self.MEMBER_NAME,
            address=self.MEMBER_ADDRESS,
            protocol_port=self.PROTOCOL_PORT, weight=self.WEIGHT)
        assert isinstance(test_member, member.Member)
        self.assertEqual(self.MEMBER_NAME, test_member.name)
        self.MEMBER_ID = test_member.id
        self.conn.load_balancer.wait_for_load_balancer(self.LB_ID)

        test_hm = self.conn.load_balancer.create_health_monitor(
            pool_id=self.POOL_ID, name=self.HM_NAME, delay=self.DELAY,
            timeout=self.TIMEOUT, max_retries=self.MAX_RETRY,
            type=self.HM_TYPE)
        assert isinstance(test_hm, health_monitor.HealthMonitor)
        self.assertEqual(self.HM_NAME, test_hm.name)
        self.HM_ID = test_hm.id
        self.conn.load_balancer.wait_for_load_balancer(self.LB_ID)

        test_l7policy = self.conn.load_balancer.create_l7_policy(
            listener_id=self.LISTENER_ID, name=self.L7POLICY_NAME,
            action=self.ACTION, redirect_url=self.REDIRECT_URL)
        assert isinstance(test_l7policy, l7_policy.L7Policy)
        self.assertEqual(self.L7POLICY_NAME, test_l7policy.name)
        self.L7POLICY_ID = test_l7policy.id
        self.conn.load_balancer.wait_for_load_balancer(self.LB_ID)

        test_l7rule = self.conn.load_balancer.create_l7_rule(
            l7_policy=self.L7POLICY_ID, compare_type=self.COMPARE_TYPE,
            type=self.L7RULE_TYPE, value=self.L7RULE_VALUE)
        assert isinstance(test_l7rule, l7_rule.L7Rule)
        self.assertEqual(self.COMPARE_TYPE, test_l7rule.compare_type)
        self.L7RULE_ID = test_l7rule.id
        self.conn.load_balancer.wait_for_load_balancer(self.LB_ID)

    def tearDown(self):
        self.conn.load_balancer.get_load_balancer(self.LB_ID)
        self.conn.load_balancer.wait_for_load_balancer(self.LB_ID)

        self.conn.load_balancer.delete_l7_rule(
            self.L7RULE_ID, l7_policy=self.L7POLICY_ID, ignore_missing=False)
        self.conn.load_balancer.wait_for_load_balancer(self.LB_ID)

        self.conn.load_balancer.delete_l7_policy(
            self.L7POLICY_ID, ignore_missing=False)
        self.conn.load_balancer.wait_for_load_balancer(self.LB_ID)

        self.conn.load_balancer.delete_health_monitor(
            self.HM_ID, ignore_missing=False)
        self.conn.load_balancer.wait_for_load_balancer(self.LB_ID)

        self.conn.load_balancer.delete_member(
            self.MEMBER_ID, self.POOL_ID, ignore_missing=False)
        self.conn.load_balancer.wait_for_load_balancer(self.LB_ID)

        self.conn.load_balancer.delete_pool(self.POOL_ID, ignore_missing=False)
        self.conn.load_balancer.wait_for_load_balancer(self.LB_ID)

        self.conn.load_balancer.delete_listener(self.LISTENER_ID,
                                                ignore_missing=False)
        self.conn.load_balancer.wait_for_load_balancer(self.LB_ID)

        self.conn.load_balancer.delete_load_balancer(
            self.LB_ID, ignore_missing=False)
        super(TestLoadBalancer, self).tearDown()

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
        self.conn.load_balancer.update_load_balancer(
            self.LB_ID, name=self.UPDATE_NAME)
        self.conn.load_balancer.wait_for_load_balancer(self.LB_ID)
        test_lb = self.conn.load_balancer.get_load_balancer(self.LB_ID)
        self.assertEqual(self.UPDATE_NAME, test_lb.name)

        self.conn.load_balancer.update_load_balancer(
            self.LB_ID, name=self.LB_NAME)
        self.conn.load_balancer.wait_for_load_balancer(self.LB_ID)
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
        self.conn.load_balancer.get_load_balancer(self.LB_ID)

        self.conn.load_balancer.update_listener(
            self.LISTENER_ID, name=self.UPDATE_NAME)
        self.conn.load_balancer.wait_for_load_balancer(self.LB_ID)
        test_listener = self.conn.load_balancer.get_listener(self.LISTENER_ID)
        self.assertEqual(self.UPDATE_NAME, test_listener.name)

        self.conn.load_balancer.update_listener(
            self.LISTENER_ID, name=self.LISTENER_NAME)
        self.conn.load_balancer.wait_for_load_balancer(self.LB_ID)
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
        self.conn.load_balancer.get_load_balancer(self.LB_ID)

        self.conn.load_balancer.update_pool(self.POOL_ID,
                                            name=self.UPDATE_NAME)
        self.conn.load_balancer.wait_for_load_balancer(self.LB_ID)
        test_pool = self.conn.load_balancer.get_pool(self.POOL_ID)
        self.assertEqual(self.UPDATE_NAME, test_pool.name)

        self.conn.load_balancer.update_pool(self.POOL_ID,
                                            name=self.POOL_NAME)
        self.conn.load_balancer.wait_for_load_balancer(self.LB_ID)
        test_pool = self.conn.load_balancer.get_pool(self.POOL_ID)
        self.assertEqual(self.POOL_NAME, test_pool.name)

    def test_member_find(self):
        test_member = self.conn.load_balancer.find_member(self.MEMBER_NAME,
                                                          self.POOL_ID)
        self.assertEqual(self.MEMBER_ID, test_member.id)

    def test_member_get(self):
        test_member = self.conn.load_balancer.get_member(self.MEMBER_ID,
                                                         self.POOL_ID)
        self.assertEqual(self.MEMBER_NAME, test_member.name)
        self.assertEqual(self.MEMBER_ID, test_member.id)
        self.assertEqual(self.MEMBER_ADDRESS, test_member.address)
        self.assertEqual(self.PROTOCOL_PORT, test_member.protocol_port)
        self.assertEqual(self.WEIGHT, test_member.weight)

    def test_member_list(self):
        names = [mb.name for mb in self.conn.load_balancer.members(
            self.POOL_ID)]
        self.assertIn(self.MEMBER_NAME, names)

    def test_member_update(self):
        self.conn.load_balancer.get_load_balancer(self.LB_ID)

        self.conn.load_balancer.update_member(self.MEMBER_ID, self.POOL_ID,
                                              name=self.UPDATE_NAME)
        self.conn.load_balancer.wait_for_load_balancer(self.LB_ID)
        test_member = self.conn.load_balancer.get_member(self.MEMBER_ID,
                                                         self.POOL_ID)
        self.assertEqual(self.UPDATE_NAME, test_member.name)

        self.conn.load_balancer.update_member(self.MEMBER_ID, self.POOL_ID,
                                              name=self.MEMBER_NAME)
        self.conn.load_balancer.wait_for_load_balancer(self.LB_ID)
        test_member = self.conn.load_balancer.get_member(self.MEMBER_ID,
                                                         self.POOL_ID)
        self.assertEqual(self.MEMBER_NAME, test_member.name)

    def test_health_monitor_find(self):
        test_hm = self.conn.load_balancer.find_health_monitor(self.HM_NAME)
        self.assertEqual(self.HM_ID, test_hm.id)

    def test_health_monitor_get(self):
        test_hm = self.conn.load_balancer.get_health_monitor(self.HM_ID)
        self.assertEqual(self.HM_NAME, test_hm.name)
        self.assertEqual(self.HM_ID, test_hm.id)
        self.assertEqual(self.DELAY, test_hm.delay)
        self.assertEqual(self.TIMEOUT, test_hm.timeout)
        self.assertEqual(self.MAX_RETRY, test_hm.max_retries)
        self.assertEqual(self.HM_TYPE, test_hm.type)

    def test_health_monitor_list(self):
        names = [hm.name for hm in self.conn.load_balancer.health_monitors()]
        self.assertIn(self.HM_NAME, names)

    def test_health_monitor_update(self):
        self.conn.load_balancer.get_load_balancer(self.LB_ID)

        self.conn.load_balancer.update_health_monitor(self.HM_ID,
                                                      name=self.UPDATE_NAME)
        self.conn.load_balancer.wait_for_load_balancer(self.LB_ID)
        test_hm = self.conn.load_balancer.get_health_monitor(self.HM_ID)
        self.assertEqual(self.UPDATE_NAME, test_hm.name)

        self.conn.load_balancer.update_health_monitor(self.HM_ID,
                                                      name=self.HM_NAME)
        self.conn.load_balancer.wait_for_load_balancer(self.LB_ID)
        test_hm = self.conn.load_balancer.get_health_monitor(self.HM_ID)
        self.assertEqual(self.HM_NAME, test_hm.name)

    def test_l7_policy_find(self):
        test_l7_policy = self.conn.load_balancer.find_l7_policy(
            self.L7POLICY_NAME)
        self.assertEqual(self.L7POLICY_ID, test_l7_policy.id)

    def test_l7_policy_get(self):
        test_l7_policy = self.conn.load_balancer.get_l7_policy(
            self.L7POLICY_ID)
        self.assertEqual(self.L7POLICY_NAME, test_l7_policy.name)
        self.assertEqual(self.L7POLICY_ID, test_l7_policy.id)
        self.assertEqual(self.ACTION, test_l7_policy.action)

    def test_l7_policy_list(self):
        names = [l7.name for l7 in self.conn.load_balancer.l7_policies()]
        self.assertIn(self.L7POLICY_NAME, names)

    def test_l7_policy_update(self):
        self.conn.load_balancer.get_load_balancer(self.LB_ID)

        self.conn.load_balancer.update_l7_policy(
            self.L7POLICY_ID, name=self.UPDATE_NAME)
        self.conn.load_balancer.wait_for_load_balancer(self.LB_ID)
        test_l7_policy = self.conn.load_balancer.get_l7_policy(
            self.L7POLICY_ID)
        self.assertEqual(self.UPDATE_NAME, test_l7_policy.name)

        self.conn.load_balancer.update_l7_policy(self.L7POLICY_ID,
                                                 name=self.L7POLICY_NAME)
        self.conn.load_balancer.wait_for_load_balancer(self.LB_ID)
        test_l7_policy = self.conn.load_balancer.get_l7_policy(
            self.L7POLICY_ID)
        self.assertEqual(self.L7POLICY_NAME, test_l7_policy.name)

    def test_l7_rule_find(self):
        test_l7_rule = self.conn.load_balancer.find_l7_rule(
            self.L7RULE_ID, self.L7POLICY_ID)
        self.assertEqual(self.L7RULE_ID, test_l7_rule.id)
        self.assertEqual(self.L7RULE_TYPE, test_l7_rule.type)

    def test_l7_rule_get(self):
        test_l7_rule = self.conn.load_balancer.get_l7_rule(
            self.L7RULE_ID, l7_policy=self.L7POLICY_ID)
        self.assertEqual(self.L7RULE_ID, test_l7_rule.id)
        self.assertEqual(self.COMPARE_TYPE, test_l7_rule.compare_type)
        self.assertEqual(self.L7RULE_TYPE, test_l7_rule.type)
        self.assertEqual(self.L7RULE_VALUE, test_l7_rule.rule_value)

    def test_l7_rule_list(self):
        ids = [l7.id for l7 in self.conn.load_balancer.l7_rules(
            l7_policy=self.L7POLICY_ID)]
        self.assertIn(self.L7RULE_ID, ids)

    def test_l7_rule_update(self):
        self.conn.load_balancer.get_load_balancer(self.LB_ID)

        self.conn.load_balancer.update_l7_rule(self.L7RULE_ID,
                                               l7_policy=self.L7POLICY_ID,
                                               rule_value=self.UPDATE_NAME)
        self.conn.load_balancer.wait_for_load_balancer(self.LB_ID)
        test_l7_rule = self.conn.load_balancer.get_l7_rule(
            self.L7RULE_ID, l7_policy=self.L7POLICY_ID)
        self.assertEqual(self.UPDATE_NAME, test_l7_rule.rule_value)

        self.conn.load_balancer.update_l7_rule(self.L7RULE_ID,
                                               l7_policy=self.L7POLICY_ID,
                                               rule_value=self.L7RULE_VALUE)
        self.conn.load_balancer.wait_for_load_balancer(self.LB_ID)
        test_l7_rule = self.conn.load_balancer.get_l7_rule(
            self.L7RULE_ID, l7_policy=self.L7POLICY_ID,)
        self.assertEqual(self.L7RULE_VALUE, test_l7_rule.rule_value)
