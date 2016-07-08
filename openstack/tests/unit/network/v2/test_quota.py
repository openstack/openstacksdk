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

import testtools

from openstack.network.v2 import quota

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'floatingip': 1,
    'network': 2,
    'port': 3,
    'tenant_id': '4',
    'router': 5,
    'subnet': 6,
    'subnetpool': 7,
    'security_group_rule': 8,
    'security_group': 9,
    'rbac_policy': -1,
    'healthmonitor': 11,
    'listener': 12,
    'loadbalancer': 13,
    'l7policy': 14,
    'pool': 15,
}


class TestQuota(testtools.TestCase):

    def test_basic(self):
        sot = quota.Quota()
        self.assertEqual('quota', sot.resource_key)
        self.assertEqual('quotas', sot.resources_key)
        self.assertEqual('/quotas', sot.base_path)
        self.assertEqual('network', sot.service.service_type)
        self.assertFalse(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = quota.Quota(EXAMPLE)
        self.assertEqual(EXAMPLE['floatingip'], sot.floating_ips)
        self.assertEqual(EXAMPLE['network'], sot.networks)
        self.assertEqual(EXAMPLE['port'], sot.ports)
        self.assertEqual(EXAMPLE['tenant_id'], sot.project_id)
        self.assertEqual(EXAMPLE['router'], sot.routers)
        self.assertEqual(EXAMPLE['subnet'], sot.subnets)
        self.assertEqual(EXAMPLE['subnetpool'], sot.subnet_pools)
        self.assertEqual(EXAMPLE['security_group_rule'],
                         sot.security_group_rules)
        self.assertEqual(EXAMPLE['security_group'], sot.security_groups)
        self.assertEqual(EXAMPLE['rbac_policy'], sot.rbac_policies)
        self.assertEqual(EXAMPLE['healthmonitor'], sot.health_monitors)
        self.assertEqual(EXAMPLE['listener'], sot.listeners)
        self.assertEqual(EXAMPLE['loadbalancer'], sot.load_balancers)
        self.assertEqual(EXAMPLE['l7policy'], sot.l7_policies)
        self.assertEqual(EXAMPLE['pool'], sot.pools)


class TestQuotaDefault(testtools.TestCase):

    def test_basic(self):
        default = quota.QuotaDefault()
        self.assertEqual('quota', default.resource_key)
        self.assertEqual('quotas', default.resources_key)
        self.assertEqual('/quotas/%(project)s/default', default.base_path)
        self.assertEqual('network', default.service.service_type)
        self.assertFalse(default.allow_create)
        self.assertTrue(default.allow_retrieve)
        self.assertFalse(default.allow_update)
        self.assertFalse(default.allow_delete)
        self.assertFalse(default.allow_list)

    def test_make_it(self):
        default = quota.Quota(EXAMPLE)
        self.assertEqual(EXAMPLE['floatingip'], default.floating_ips)
        self.assertEqual(EXAMPLE['network'], default.networks)
        self.assertEqual(EXAMPLE['port'], default.ports)
        self.assertEqual(EXAMPLE['tenant_id'], default.project_id)
        self.assertEqual(EXAMPLE['router'], default.routers)
        self.assertEqual(EXAMPLE['subnet'], default.subnets)
        self.assertEqual(EXAMPLE['subnetpool'], default.subnet_pools)
        self.assertEqual(EXAMPLE['security_group_rule'],
                         default.security_group_rules)
        self.assertEqual(EXAMPLE['security_group'], default.security_groups)
        self.assertEqual(EXAMPLE['rbac_policy'], default.rbac_policies)
        self.assertEqual(EXAMPLE['healthmonitor'], default.health_monitors)
        self.assertEqual(EXAMPLE['listener'], default.listeners)
        self.assertEqual(EXAMPLE['loadbalancer'], default.load_balancers)
        self.assertEqual(EXAMPLE['l7policy'], default.l7_policies)
        self.assertEqual(EXAMPLE['pool'], default.pools)
