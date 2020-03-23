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

from openstack.load_balancer.v2 import availability_zone
from openstack.load_balancer.v2 import availability_zone_profile
from openstack.load_balancer.v2 import flavor
from openstack.load_balancer.v2 import flavor_profile
from openstack.load_balancer.v2 import health_monitor
from openstack.load_balancer.v2 import l7_policy
from openstack.load_balancer.v2 import l7_rule
from openstack.load_balancer.v2 import listener
from openstack.load_balancer.v2 import load_balancer
from openstack.load_balancer.v2 import member
from openstack.load_balancer.v2 import pool
from openstack.load_balancer.v2 import quota
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
    FLAVOR_PROFILE_ID = None
    FLAVOR_ID = None
    AVAILABILITY_ZONE_PROFILE_ID = None
    AMPHORA_ID = None
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
    AMPHORA = 'amphora'
    FLAVOR_DATA = '{"loadbalancer_topology": "SINGLE"}'
    AVAILABILITY_ZONE_DATA = '{"compute_zone": "nova"}'
    DESCRIPTION = 'Test description'

    _wait_for_timeout_key = 'OPENSTACKSDK_FUNC_TEST_TIMEOUT_LOAD_BALANCER'

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
        self.UPDATE_DESCRIPTION = self.getUniqueString()
        self.FLAVOR_PROFILE_NAME = self.getUniqueString()
        self.FLAVOR_NAME = self.getUniqueString()
        self.AVAILABILITY_ZONE_PROFILE_NAME = self.getUniqueString()
        self.AVAILABILITY_ZONE_NAME = self.getUniqueString()
        subnets = list(self.conn.network.subnets())
        self.VIP_SUBNET_ID = subnets[0].id
        self.PROJECT_ID = self.conn.session.get_project_id()
        test_quota = self.conn.load_balancer.update_quota(
            self.PROJECT_ID, **{'load_balancer': 100,
                                'pool': 100,
                                'listener': 100,
                                'health_monitor': 100,
                                'member': 100})
        assert isinstance(test_quota, quota.Quota)
        self.assertEqual(self.PROJECT_ID, test_quota.id)

        test_flavor_profile = self.conn.load_balancer.create_flavor_profile(
            name=self.FLAVOR_PROFILE_NAME, provider_name=self.AMPHORA,
            flavor_data=self.FLAVOR_DATA)
        assert isinstance(test_flavor_profile, flavor_profile.FlavorProfile)
        self.assertEqual(self.FLAVOR_PROFILE_NAME, test_flavor_profile.name)
        self.FLAVOR_PROFILE_ID = test_flavor_profile.id

        test_flavor = self.conn.load_balancer.create_flavor(
            name=self.FLAVOR_NAME, flavor_profile_id=self.FLAVOR_PROFILE_ID,
            is_enabled=True, description=self.DESCRIPTION)
        assert isinstance(test_flavor, flavor.Flavor)
        self.assertEqual(self.FLAVOR_NAME, test_flavor.name)
        self.FLAVOR_ID = test_flavor.id

        test_az_profile = \
            self.conn.load_balancer.create_availability_zone_profile(
                name=self.AVAILABILITY_ZONE_PROFILE_NAME,
                provider_name=self.AMPHORA,
                availability_zone_data=self.AVAILABILITY_ZONE_DATA)
        assert isinstance(test_az_profile,
                          availability_zone_profile.AvailabilityZoneProfile)
        self.assertEqual(self.AVAILABILITY_ZONE_PROFILE_NAME,
                         test_az_profile.name)
        self.AVAILABILITY_ZONE_PROFILE_ID = test_az_profile.id

        test_az = self.conn.load_balancer.create_availability_zone(
            name=self.AVAILABILITY_ZONE_NAME,
            availability_zone_profile_id=self.AVAILABILITY_ZONE_PROFILE_ID,
            is_enabled=True, description=self.DESCRIPTION)
        assert isinstance(test_az, availability_zone.AvailabilityZone)
        self.assertEqual(self.AVAILABILITY_ZONE_NAME, test_az.name)

        test_lb = self.conn.load_balancer.create_load_balancer(
            name=self.LB_NAME, vip_subnet_id=self.VIP_SUBNET_ID,
            project_id=self.PROJECT_ID)
        assert isinstance(test_lb, load_balancer.LoadBalancer)
        self.assertEqual(self.LB_NAME, test_lb.name)
        # Wait for the LB to go ACTIVE.  On non-virtualization enabled hosts
        # it can take nova up to ten minutes to boot a VM.
        self.conn.load_balancer.wait_for_load_balancer(
            test_lb.id, interval=1,
            wait=self._wait_for_timeout)
        self.LB_ID = test_lb.id

        amphorae = self.conn.load_balancer.amphorae(loadbalancer_id=self.LB_ID)
        for amp in amphorae:
            self.AMPHORA_ID = amp.id

        test_listener = self.conn.load_balancer.create_listener(
            name=self.LISTENER_NAME, protocol=self.PROTOCOL,
            protocol_port=self.PROTOCOL_PORT, loadbalancer_id=self.LB_ID)
        assert isinstance(test_listener, listener.Listener)
        self.assertEqual(self.LISTENER_NAME, test_listener.name)
        self.LISTENER_ID = test_listener.id
        self.conn.load_balancer.wait_for_load_balancer(
            self.LB_ID, wait=self._wait_for_timeout)

        test_pool = self.conn.load_balancer.create_pool(
            name=self.POOL_NAME, protocol=self.PROTOCOL,
            lb_algorithm=self.LB_ALGORITHM, listener_id=self.LISTENER_ID)
        assert isinstance(test_pool, pool.Pool)
        self.assertEqual(self.POOL_NAME, test_pool.name)
        self.POOL_ID = test_pool.id
        self.conn.load_balancer.wait_for_load_balancer(
            self.LB_ID, wait=self._wait_for_timeout)

        test_member = self.conn.load_balancer.create_member(
            pool=self.POOL_ID, name=self.MEMBER_NAME,
            address=self.MEMBER_ADDRESS,
            protocol_port=self.PROTOCOL_PORT, weight=self.WEIGHT)
        assert isinstance(test_member, member.Member)
        self.assertEqual(self.MEMBER_NAME, test_member.name)
        self.MEMBER_ID = test_member.id
        self.conn.load_balancer.wait_for_load_balancer(
            self.LB_ID, wait=self._wait_for_timeout)

        test_hm = self.conn.load_balancer.create_health_monitor(
            pool_id=self.POOL_ID, name=self.HM_NAME, delay=self.DELAY,
            timeout=self.TIMEOUT, max_retries=self.MAX_RETRY,
            type=self.HM_TYPE)
        assert isinstance(test_hm, health_monitor.HealthMonitor)
        self.assertEqual(self.HM_NAME, test_hm.name)
        self.HM_ID = test_hm.id
        self.conn.load_balancer.wait_for_load_balancer(
            self.LB_ID, wait=self._wait_for_timeout)

        test_l7policy = self.conn.load_balancer.create_l7_policy(
            listener_id=self.LISTENER_ID, name=self.L7POLICY_NAME,
            action=self.ACTION, redirect_url=self.REDIRECT_URL)
        assert isinstance(test_l7policy, l7_policy.L7Policy)
        self.assertEqual(self.L7POLICY_NAME, test_l7policy.name)
        self.L7POLICY_ID = test_l7policy.id
        self.conn.load_balancer.wait_for_load_balancer(
            self.LB_ID, wait=self._wait_for_timeout)

        test_l7rule = self.conn.load_balancer.create_l7_rule(
            l7_policy=self.L7POLICY_ID, compare_type=self.COMPARE_TYPE,
            type=self.L7RULE_TYPE, value=self.L7RULE_VALUE)
        assert isinstance(test_l7rule, l7_rule.L7Rule)
        self.assertEqual(self.COMPARE_TYPE, test_l7rule.compare_type)
        self.L7RULE_ID = test_l7rule.id
        self.conn.load_balancer.wait_for_load_balancer(
            self.LB_ID, wait=self._wait_for_timeout)

    def tearDown(self):
        self.conn.load_balancer.get_load_balancer(self.LB_ID)
        self.conn.load_balancer.wait_for_load_balancer(
            self.LB_ID, wait=self._wait_for_timeout)

        self.conn.load_balancer.delete_quota(self.PROJECT_ID,
                                             ignore_missing=False)

        self.conn.load_balancer.delete_l7_rule(
            self.L7RULE_ID, l7_policy=self.L7POLICY_ID, ignore_missing=False)
        self.conn.load_balancer.wait_for_load_balancer(
            self.LB_ID, wait=self._wait_for_timeout)

        self.conn.load_balancer.delete_l7_policy(
            self.L7POLICY_ID, ignore_missing=False)
        self.conn.load_balancer.wait_for_load_balancer(
            self.LB_ID, wait=self._wait_for_timeout)

        self.conn.load_balancer.delete_health_monitor(
            self.HM_ID, ignore_missing=False)
        self.conn.load_balancer.wait_for_load_balancer(
            self.LB_ID, wait=self._wait_for_timeout)

        self.conn.load_balancer.delete_member(
            self.MEMBER_ID, self.POOL_ID, ignore_missing=False)
        self.conn.load_balancer.wait_for_load_balancer(
            self.LB_ID, wait=self._wait_for_timeout)

        self.conn.load_balancer.delete_pool(self.POOL_ID, ignore_missing=False)
        self.conn.load_balancer.wait_for_load_balancer(
            self.LB_ID, wait=self._wait_for_timeout)

        self.conn.load_balancer.delete_listener(self.LISTENER_ID,
                                                ignore_missing=False)
        self.conn.load_balancer.wait_for_load_balancer(
            self.LB_ID, wait=self._wait_for_timeout)

        self.conn.load_balancer.delete_load_balancer(
            self.LB_ID, ignore_missing=False)
        super(TestLoadBalancer, self).tearDown()

        self.conn.load_balancer.delete_flavor(self.FLAVOR_ID,
                                              ignore_missing=False)

        self.conn.load_balancer.delete_flavor_profile(self.FLAVOR_PROFILE_ID,
                                                      ignore_missing=False)

        self.conn.load_balancer.delete_availability_zone(
            self.AVAILABILITY_ZONE_NAME, ignore_missing=False)

        self.conn.load_balancer.delete_availability_zone_profile(
            self.AVAILABILITY_ZONE_PROFILE_ID, ignore_missing=False)

    def test_lb_find(self):
        test_lb = self.conn.load_balancer.find_load_balancer(self.LB_NAME)
        self.assertEqual(self.LB_ID, test_lb.id)

    def test_lb_get(self):
        test_lb = self.conn.load_balancer.get_load_balancer(self.LB_ID)
        self.assertEqual(self.LB_NAME, test_lb.name)
        self.assertEqual(self.LB_ID, test_lb.id)
        self.assertEqual(self.VIP_SUBNET_ID, test_lb.vip_subnet_id)

    def test_lb_get_stats(self):
        test_lb_stats = self.conn.load_balancer.get_load_balancer_statistics(
            self.LB_ID)
        self.assertEqual(0, test_lb_stats.active_connections)
        self.assertEqual(0, test_lb_stats.bytes_in)
        self.assertEqual(0, test_lb_stats.bytes_out)
        self.assertEqual(0, test_lb_stats.request_errors)
        self.assertEqual(0, test_lb_stats.total_connections)

    def test_lb_list(self):
        names = [lb.name for lb in self.conn.load_balancer.load_balancers()]
        self.assertIn(self.LB_NAME, names)

    def test_lb_update(self):
        self.conn.load_balancer.update_load_balancer(
            self.LB_ID, name=self.UPDATE_NAME)
        self.conn.load_balancer.wait_for_load_balancer(
            self.LB_ID, wait=self._wait_for_timeout)
        test_lb = self.conn.load_balancer.get_load_balancer(self.LB_ID)
        self.assertEqual(self.UPDATE_NAME, test_lb.name)

        self.conn.load_balancer.update_load_balancer(
            self.LB_ID, name=self.LB_NAME)
        self.conn.load_balancer.wait_for_load_balancer(
            self.LB_ID, wait=self._wait_for_timeout)
        test_lb = self.conn.load_balancer.get_load_balancer(self.LB_ID)
        self.assertEqual(self.LB_NAME, test_lb.name)

    def test_lb_failover(self):
        self.conn.load_balancer.failover_load_balancer(self.LB_ID)
        self.conn.load_balancer.wait_for_load_balancer(
            self.LB_ID, wait=self._wait_for_timeout)
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

    def test_listener_get_stats(self):
        test_listener_stats = self.conn.load_balancer.get_listener_statistics(
            self.LISTENER_ID)
        self.assertEqual(0, test_listener_stats.active_connections)
        self.assertEqual(0, test_listener_stats.bytes_in)
        self.assertEqual(0, test_listener_stats.bytes_out)
        self.assertEqual(0, test_listener_stats.request_errors)
        self.assertEqual(0, test_listener_stats.total_connections)

    def test_listener_list(self):
        names = [ls.name for ls in self.conn.load_balancer.listeners()]
        self.assertIn(self.LISTENER_NAME, names)

    def test_listener_update(self):
        self.conn.load_balancer.get_load_balancer(self.LB_ID)

        self.conn.load_balancer.update_listener(
            self.LISTENER_ID, name=self.UPDATE_NAME)
        self.conn.load_balancer.wait_for_load_balancer(
            self.LB_ID, wait=self._wait_for_timeout)
        test_listener = self.conn.load_balancer.get_listener(self.LISTENER_ID)
        self.assertEqual(self.UPDATE_NAME, test_listener.name)

        self.conn.load_balancer.update_listener(
            self.LISTENER_ID, name=self.LISTENER_NAME)
        self.conn.load_balancer.wait_for_load_balancer(
            self.LB_ID, wait=self._wait_for_timeout)
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
        self.conn.load_balancer.wait_for_load_balancer(
            self.LB_ID, wait=self._wait_for_timeout)
        test_pool = self.conn.load_balancer.get_pool(self.POOL_ID)
        self.assertEqual(self.UPDATE_NAME, test_pool.name)

        self.conn.load_balancer.update_pool(self.POOL_ID,
                                            name=self.POOL_NAME)
        self.conn.load_balancer.wait_for_load_balancer(
            self.LB_ID, wait=self._wait_for_timeout)
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
        self.conn.load_balancer.wait_for_load_balancer(
            self.LB_ID, wait=self._wait_for_timeout)
        test_member = self.conn.load_balancer.get_member(self.MEMBER_ID,
                                                         self.POOL_ID)
        self.assertEqual(self.UPDATE_NAME, test_member.name)

        self.conn.load_balancer.update_member(self.MEMBER_ID, self.POOL_ID,
                                              name=self.MEMBER_NAME)
        self.conn.load_balancer.wait_for_load_balancer(
            self.LB_ID, wait=self._wait_for_timeout)
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
        self.conn.load_balancer.wait_for_load_balancer(
            self.LB_ID, wait=self._wait_for_timeout)
        test_hm = self.conn.load_balancer.get_health_monitor(self.HM_ID)
        self.assertEqual(self.UPDATE_NAME, test_hm.name)

        self.conn.load_balancer.update_health_monitor(self.HM_ID,
                                                      name=self.HM_NAME)
        self.conn.load_balancer.wait_for_load_balancer(
            self.LB_ID, wait=self._wait_for_timeout)
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
        self.conn.load_balancer.wait_for_load_balancer(
            self.LB_ID, wait=self._wait_for_timeout)
        test_l7_policy = self.conn.load_balancer.get_l7_policy(
            self.L7POLICY_ID)
        self.assertEqual(self.UPDATE_NAME, test_l7_policy.name)

        self.conn.load_balancer.update_l7_policy(self.L7POLICY_ID,
                                                 name=self.L7POLICY_NAME)
        self.conn.load_balancer.wait_for_load_balancer(
            self.LB_ID, wait=self._wait_for_timeout)
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
        self.conn.load_balancer.wait_for_load_balancer(
            self.LB_ID, wait=self._wait_for_timeout)
        test_l7_rule = self.conn.load_balancer.get_l7_rule(
            self.L7RULE_ID, l7_policy=self.L7POLICY_ID)
        self.assertEqual(self.UPDATE_NAME, test_l7_rule.rule_value)

        self.conn.load_balancer.update_l7_rule(self.L7RULE_ID,
                                               l7_policy=self.L7POLICY_ID,
                                               rule_value=self.L7RULE_VALUE)
        self.conn.load_balancer.wait_for_load_balancer(
            self.LB_ID, wait=self._wait_for_timeout)
        test_l7_rule = self.conn.load_balancer.get_l7_rule(
            self.L7RULE_ID, l7_policy=self.L7POLICY_ID,)
        self.assertEqual(self.L7RULE_VALUE, test_l7_rule.rule_value)

    def test_quota_list(self):
        for qot in self.conn.load_balancer.quotas():
            self.assertIsNotNone(qot.project_id)

    def test_quota_get(self):
        test_quota = self.conn.load_balancer.get_quota(self.PROJECT_ID)
        self.assertEqual(self.PROJECT_ID, test_quota.id)

    def test_quota_update(self):
        attrs = {'load_balancer': 12345, 'pool': 67890}
        for project_quota in self.conn.load_balancer.quotas():
            self.conn.load_balancer.update_quota(project_quota, **attrs)
            new_quota = self.conn.load_balancer.get_quota(
                project_quota.project_id)
            self.assertEqual(12345, new_quota.load_balancers)
            self.assertEqual(67890, new_quota.pools)

    def test_default_quota(self):
        self.conn.load_balancer.get_quota_default()

    def test_providers(self):
        providers = self.conn.load_balancer.providers()
        # Make sure our default provider is in the list
        self.assertTrue(
            any(prov['name'] == self.AMPHORA for prov in providers))

    def test_provider_flavor_capabilities(self):
        capabilities = self.conn.load_balancer.provider_flavor_capabilities(
            self.AMPHORA)
        # Make sure a known capability is in the default provider
        self.assertTrue(any(
            cap['name'] == 'loadbalancer_topology' for cap in capabilities))

    def test_flavor_profile_find(self):
        test_profile = self.conn.load_balancer.find_flavor_profile(
            self.FLAVOR_PROFILE_NAME)
        self.assertEqual(self.FLAVOR_PROFILE_ID, test_profile.id)

    def test_flavor_profile_get(self):
        test_flavor_profile = self.conn.load_balancer.get_flavor_profile(
            self.FLAVOR_PROFILE_ID)
        self.assertEqual(self.FLAVOR_PROFILE_NAME, test_flavor_profile.name)
        self.assertEqual(self.FLAVOR_PROFILE_ID, test_flavor_profile.id)
        self.assertEqual(self.AMPHORA, test_flavor_profile.provider_name)
        self.assertEqual(self.FLAVOR_DATA, test_flavor_profile.flavor_data)

    def test_flavor_profile_list(self):
        names = [fv.name for fv in self.conn.load_balancer.flavor_profiles()]
        self.assertIn(self.FLAVOR_PROFILE_NAME, names)

    def test_flavor_profile_update(self):
        self.conn.load_balancer.update_flavor_profile(
            self.FLAVOR_PROFILE_ID, name=self.UPDATE_NAME)
        test_flavor_profile = self.conn.load_balancer.get_flavor_profile(
            self.FLAVOR_PROFILE_ID)
        self.assertEqual(self.UPDATE_NAME, test_flavor_profile.name)

        self.conn.load_balancer.update_flavor_profile(
            self.FLAVOR_PROFILE_ID, name=self.FLAVOR_PROFILE_NAME)
        test_flavor_profile = self.conn.load_balancer.get_flavor_profile(
            self.FLAVOR_PROFILE_ID)
        self.assertEqual(self.FLAVOR_PROFILE_NAME, test_flavor_profile.name)

    def test_flavor_find(self):
        test_flavor = self.conn.load_balancer.find_flavor(self.FLAVOR_NAME)
        self.assertEqual(self.FLAVOR_ID, test_flavor.id)

    def test_flavor_get(self):
        test_flavor = self.conn.load_balancer.get_flavor(self.FLAVOR_ID)
        self.assertEqual(self.FLAVOR_NAME, test_flavor.name)
        self.assertEqual(self.FLAVOR_ID, test_flavor.id)
        self.assertEqual(self.DESCRIPTION, test_flavor.description)
        self.assertEqual(self.FLAVOR_PROFILE_ID, test_flavor.flavor_profile_id)

    def test_flavor_list(self):
        names = [fv.name for fv in self.conn.load_balancer.flavors()]
        self.assertIn(self.FLAVOR_NAME, names)

    def test_flavor_update(self):
        self.conn.load_balancer.update_flavor(
            self.FLAVOR_ID, name=self.UPDATE_NAME)
        test_flavor = self.conn.load_balancer.get_flavor(self.FLAVOR_ID)
        self.assertEqual(self.UPDATE_NAME, test_flavor.name)

        self.conn.load_balancer.update_flavor(
            self.FLAVOR_ID, name=self.FLAVOR_NAME)
        test_flavor = self.conn.load_balancer.get_flavor(self.FLAVOR_ID)
        self.assertEqual(self.FLAVOR_NAME, test_flavor.name)

    def test_amphora_list(self):
        amp_ids = [amp.id for amp in self.conn.load_balancer.amphorae()]
        self.assertIn(self.AMPHORA_ID, amp_ids)

    def test_amphora_find(self):
        test_amphora = self.conn.load_balancer.find_amphora(self.AMPHORA_ID)
        self.assertEqual(self.AMPHORA_ID, test_amphora.id)

    def test_amphora_get(self):
        test_amphora = self.conn.load_balancer.get_amphora(self.AMPHORA_ID)
        self.assertEqual(self.AMPHORA_ID, test_amphora.id)

    def test_amphora_configure(self):
        self.conn.load_balancer.configure_amphora(self.AMPHORA_ID)
        test_amp = self.conn.load_balancer.get_amphora(self.AMPHORA_ID)
        self.assertEqual(self.AMPHORA_ID, test_amp.id)

    def test_amphora_failover(self):
        self.conn.load_balancer.failover_amphora(self.AMPHORA_ID)
        test_amp = self.conn.load_balancer.get_amphora(self.AMPHORA_ID)
        self.assertEqual(self.AMPHORA_ID, test_amp.id)

    def test_availability_zone_profile_find(self):
        test_profile = self.conn.load_balancer.find_availability_zone_profile(
            self.AVAILABILITY_ZONE_PROFILE_NAME)
        self.assertEqual(self.AVAILABILITY_ZONE_PROFILE_ID, test_profile.id)

    def test_availability_zone_profile_get(self):
        test_availability_zone_profile = \
            self.conn.load_balancer.get_availability_zone_profile(
                self.AVAILABILITY_ZONE_PROFILE_ID)
        self.assertEqual(self.AVAILABILITY_ZONE_PROFILE_NAME,
                         test_availability_zone_profile.name)
        self.assertEqual(self.AVAILABILITY_ZONE_PROFILE_ID,
                         test_availability_zone_profile.id)
        self.assertEqual(self.AMPHORA,
                         test_availability_zone_profile.provider_name)
        self.assertEqual(self.AVAILABILITY_ZONE_DATA,
                         test_availability_zone_profile.availability_zone_data)

    def test_availability_zone_profile_list(self):
        names = [az.name for az in
                 self.conn.load_balancer.availability_zone_profiles()]
        self.assertIn(self.AVAILABILITY_ZONE_PROFILE_NAME, names)

    def test_availability_zone_profile_update(self):
        self.conn.load_balancer.update_availability_zone_profile(
            self.AVAILABILITY_ZONE_PROFILE_ID, name=self.UPDATE_NAME)
        test_availability_zone_profile = \
            self.conn.load_balancer.get_availability_zone_profile(
                self.AVAILABILITY_ZONE_PROFILE_ID)
        self.assertEqual(self.UPDATE_NAME, test_availability_zone_profile.name)

        self.conn.load_balancer.update_availability_zone_profile(
            self.AVAILABILITY_ZONE_PROFILE_ID,
            name=self.AVAILABILITY_ZONE_PROFILE_NAME)
        test_availability_zone_profile = \
            self.conn.load_balancer.get_availability_zone_profile(
                self.AVAILABILITY_ZONE_PROFILE_ID)
        self.assertEqual(self.AVAILABILITY_ZONE_PROFILE_NAME,
                         test_availability_zone_profile.name)

    def test_availability_zone_find(self):
        test_availability_zone = \
            self.conn.load_balancer.find_availability_zone(
                self.AVAILABILITY_ZONE_NAME)
        self.assertEqual(self.AVAILABILITY_ZONE_NAME,
                         test_availability_zone.name)

    def test_availability_zone_get(self):
        test_availability_zone = self.conn.load_balancer.get_availability_zone(
            self.AVAILABILITY_ZONE_NAME)
        self.assertEqual(self.AVAILABILITY_ZONE_NAME,
                         test_availability_zone.name)
        self.assertEqual(self.DESCRIPTION, test_availability_zone.description)
        self.assertEqual(self.AVAILABILITY_ZONE_PROFILE_ID,
                         test_availability_zone.availability_zone_profile_id)

    def test_availability_zone_list(self):
        names = [az.name for az in
                 self.conn.load_balancer.availability_zones()]
        self.assertIn(self.AVAILABILITY_ZONE_NAME, names)

    def test_availability_zone_update(self):
        self.conn.load_balancer.update_availability_zone(
            self.AVAILABILITY_ZONE_NAME, description=self.UPDATE_DESCRIPTION)
        test_availability_zone = self.conn.load_balancer.get_availability_zone(
            self.AVAILABILITY_ZONE_NAME)
        self.assertEqual(self.UPDATE_DESCRIPTION,
                         test_availability_zone.description)

        self.conn.load_balancer.update_availability_zone(
            self.AVAILABILITY_ZONE_NAME, description=self.DESCRIPTION)
        test_availability_zone = self.conn.load_balancer.get_availability_zone(
            self.AVAILABILITY_ZONE_NAME)
        self.assertEqual(self.DESCRIPTION, test_availability_zone.description)
