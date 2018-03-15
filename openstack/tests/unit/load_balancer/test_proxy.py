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

import uuid
import mock

from openstack.load_balancer.v2 import _proxy
from openstack.load_balancer.v2 import health_monitor
from openstack.load_balancer.v2 import l7_policy
from openstack.load_balancer.v2 import l7_rule
from openstack.load_balancer.v2 import listener
from openstack.load_balancer.v2 import load_balancer as lb
from openstack.load_balancer.v2 import member
from openstack.load_balancer.v2 import pool
from openstack import proxy as proxy_base
from openstack.tests.unit import test_proxy_base


class TestLoadBalancerProxy(test_proxy_base.TestProxyBase):

    POOL_ID = uuid.uuid4()
    L7_POLICY_ID = uuid.uuid4()

    def setUp(self):
        super(TestLoadBalancerProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_load_balancers(self):
        self.verify_list(self.proxy.load_balancers,
                         lb.LoadBalancer,
                         paginated=True)

    def test_load_balancer_get(self):
        self.verify_get(self.proxy.get_load_balancer,
                        lb.LoadBalancer)

    def test_load_balancer_create(self):
        self.verify_create(self.proxy.create_load_balancer,
                           lb.LoadBalancer)

    @mock.patch.object(proxy_base.Proxy, '_get_resource')
    def test_load_balancer_delete_non_cascade(self, mock_get_resource):
        fake_load_balancer = mock.Mock()
        fake_load_balancer.id = "load_balancer_id"
        mock_get_resource.return_value = fake_load_balancer
        self._verify2("openstack.proxy.Proxy._delete",
                      self.proxy.delete_load_balancer,
                      method_args=["resource_or_id", True,
                                   False],
                      expected_args=[lb.LoadBalancer,
                                     fake_load_balancer],
                      expected_kwargs={"ignore_missing": True})
        self.assertFalse(fake_load_balancer.cascade)
        mock_get_resource.assert_called_once_with(lb.LoadBalancer,
                                                  "resource_or_id")

    @mock.patch.object(proxy_base.Proxy, '_get_resource')
    def test_load_balancer_delete_cascade(self, mock_get_resource):
        fake_load_balancer = mock.Mock()
        fake_load_balancer.id = "load_balancer_id"
        mock_get_resource.return_value = fake_load_balancer
        self._verify2("openstack.proxy.Proxy._delete",
                      self.proxy.delete_load_balancer,
                      method_args=["resource_or_id", True,
                                   True],
                      expected_args=[lb.LoadBalancer,
                                     fake_load_balancer],
                      expected_kwargs={"ignore_missing": True})
        self.assertTrue(fake_load_balancer.cascade)
        mock_get_resource.assert_called_once_with(lb.LoadBalancer,
                                                  "resource_or_id")

    def test_load_balancer_find(self):
        self.verify_find(self.proxy.find_load_balancer,
                         lb.LoadBalancer)

    def test_load_balancer_update(self):
        self.verify_update(self.proxy.update_load_balancer,
                           lb.LoadBalancer)

    def test_listeners(self):
        self.verify_list(self.proxy.listeners,
                         listener.Listener,
                         paginated=True)

    def test_listener_get(self):
        self.verify_get(self.proxy.get_listener,
                        listener.Listener)

    def test_listener_create(self):
        self.verify_create(self.proxy.create_listener,
                           listener.Listener)

    def test_listener_delete(self):
        self.verify_delete(self.proxy.delete_listener,
                           listener.Listener, True)

    def test_listener_find(self):
        self.verify_find(self.proxy.find_listener,
                         listener.Listener)

    def test_listener_update(self):
        self.verify_update(self.proxy.update_listener,
                           listener.Listener)

    def test_pools(self):
        self.verify_list(self.proxy.pools,
                         pool.Pool,
                         paginated=True)

    def test_pool_get(self):
        self.verify_get(self.proxy.get_pool,
                        pool.Pool)

    def test_pool_create(self):
        self.verify_create(self.proxy.create_pool,
                           pool.Pool)

    def test_pool_delete(self):
        self.verify_delete(self.proxy.delete_pool,
                           pool.Pool, True)

    def test_pool_find(self):
        self.verify_find(self.proxy.find_pool,
                         pool.Pool)

    def test_pool_update(self):
        self.verify_update(self.proxy.update_pool,
                           pool.Pool)

    def test_members(self):
        self.verify_list(self.proxy.members,
                         member.Member,
                         paginated=True,
                         method_kwargs={'pool': self.POOL_ID},
                         expected_kwargs={'pool_id': self.POOL_ID})

    def test_member_get(self):
        self.verify_get(self.proxy.get_member,
                        member.Member,
                        method_kwargs={'pool': self.POOL_ID},
                        expected_kwargs={'pool_id': self.POOL_ID})

    def test_member_create(self):
        self.verify_create(self.proxy.create_member,
                           member.Member,
                           method_kwargs={'pool': self.POOL_ID},
                           expected_kwargs={'pool_id': self.POOL_ID})

    def test_member_delete(self):
        self.verify_delete(self.proxy.delete_member,
                           member.Member,
                           True,
                           method_kwargs={'pool': self.POOL_ID},
                           expected_kwargs={'pool_id': self.POOL_ID})

    def test_member_find(self):
        self._verify2('openstack.proxy.Proxy._find',
                      self.proxy.find_member,
                      method_args=["MEMBER", self.POOL_ID],
                      expected_args=[member.Member, "MEMBER"],
                      expected_kwargs={"pool_id": self.POOL_ID,
                                       "ignore_missing": True})

    def test_member_update(self):
        self._verify2('openstack.proxy.Proxy._update',
                      self.proxy.update_member,
                      method_args=["MEMBER", self.POOL_ID],
                      expected_args=[member.Member, "MEMBER"],
                      expected_kwargs={"pool_id": self.POOL_ID})

    def test_health_monitors(self):
        self.verify_list(self.proxy.health_monitors,
                         health_monitor.HealthMonitor,
                         paginated=True)

    def test_health_monitor_get(self):
        self.verify_get(self.proxy.get_health_monitor,
                        health_monitor.HealthMonitor)

    def test_health_monitor_create(self):
        self.verify_create(self.proxy.create_health_monitor,
                           health_monitor.HealthMonitor)

    def test_health_monitor_delete(self):
        self.verify_delete(self.proxy.delete_health_monitor,
                           health_monitor.HealthMonitor, True)

    def test_health_monitor_find(self):
        self.verify_find(self.proxy.find_health_monitor,
                         health_monitor.HealthMonitor)

    def test_health_monitor_update(self):
        self.verify_update(self.proxy.update_health_monitor,
                           health_monitor.HealthMonitor)

    def test_l7_policies(self):
        self.verify_list(self.proxy.l7_policies,
                         l7_policy.L7Policy,
                         paginated=True)

    def test_l7_policy_get(self):
        self.verify_get(self.proxy.get_l7_policy,
                        l7_policy.L7Policy)

    def test_l7_policy_create(self):
        self.verify_create(self.proxy.create_l7_policy,
                           l7_policy.L7Policy)

    def test_l7_policy_delete(self):
        self.verify_delete(self.proxy.delete_l7_policy,
                           l7_policy.L7Policy, True)

    def test_l7_policy_find(self):
        self.verify_find(self.proxy.find_l7_policy,
                         l7_policy.L7Policy)

    def test_l7_policy_update(self):
        self.verify_update(self.proxy.update_l7_policy,
                           l7_policy.L7Policy)

    def test_l7_rules(self):
        self.verify_list(self.proxy.l7_rules,
                         l7_rule.L7Rule,
                         paginated=True,
                         method_kwargs={'l7_policy': self.L7_POLICY_ID},
                         expected_kwargs={'l7policy_id': self.L7_POLICY_ID})

    def test_l7_rule_get(self):
        self.verify_get(self.proxy.get_l7_rule,
                        l7_rule.L7Rule,
                        method_kwargs={'l7_policy': self.L7_POLICY_ID},
                        expected_kwargs={'l7policy_id': self.L7_POLICY_ID})

    def test_l7_rule_create(self):
        self.verify_create(self.proxy.create_l7_rule,
                           l7_rule.L7Rule,
                           method_kwargs={'l7_policy': self.L7_POLICY_ID},
                           expected_kwargs={'l7policy_id': self.L7_POLICY_ID})

    def test_l7_rule_delete(self):
        self.verify_delete(self.proxy.delete_l7_rule,
                           l7_rule.L7Rule,
                           True,
                           method_kwargs={'l7_policy': self.L7_POLICY_ID},
                           expected_kwargs={'l7policy_id': self.L7_POLICY_ID})

    def test_l7_rule_find(self):
        self._verify2('openstack.proxy.Proxy._find',
                      self.proxy.find_l7_rule,
                      method_args=["RULE", self.L7_POLICY_ID],
                      expected_args=[l7_rule.L7Rule, "RULE"],
                      expected_kwargs={"l7policy_id": self.L7_POLICY_ID,
                                       "ignore_missing": True})

    def test_l7_rule_update(self):
        self._verify2('openstack.proxy.Proxy._update',
                      self.proxy.update_l7_rule,
                      method_args=["RULE", self.L7_POLICY_ID],
                      expected_args=[l7_rule.L7Rule, "RULE"],
                      expected_kwargs={"l7policy_id": self.L7_POLICY_ID})
