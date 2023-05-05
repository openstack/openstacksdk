# Copyright (c) 2018 China Telecom Corporation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from openstack.load_balancer.v2 import quota
from openstack.tests.unit import base


IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'load_balancer': 1,
    'listener': 2,
    'pool': 3,
    'health_monitor': 4,
    'member': 5,
    'project_id': 6,
}


class TestQuota(base.TestCase):
    def test_basic(self):
        sot = quota.Quota()
        self.assertEqual('quota', sot.resource_key)
        self.assertEqual('quotas', sot.resources_key)
        self.assertEqual('/lbaas/quotas', sot.base_path)
        self.assertFalse(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = quota.Quota(**EXAMPLE)
        self.assertEqual(EXAMPLE['load_balancer'], sot.load_balancers)
        self.assertEqual(EXAMPLE['listener'], sot.listeners)
        self.assertEqual(EXAMPLE['pool'], sot.pools)
        self.assertEqual(EXAMPLE['health_monitor'], sot.health_monitors)
        self.assertEqual(EXAMPLE['member'], sot.members)
        self.assertEqual(EXAMPLE['project_id'], sot.project_id)

    def test_prepare_request(self):
        body = {'id': 'ABCDEFGH', 'load_balancer': '12345'}
        quota_obj = quota.Quota(**body)
        response = quota_obj._prepare_request()
        self.assertNotIn('id', response)


class TestQuotaDefault(base.TestCase):
    def test_basic(self):
        sot = quota.QuotaDefault()
        self.assertEqual('quota', sot.resource_key)
        self.assertEqual('quotas', sot.resources_key)
        self.assertEqual('/lbaas/quotas/defaults', sot.base_path)
        self.assertFalse(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertFalse(sot.allow_delete)
        self.assertFalse(sot.allow_list)
        self.assertTrue(sot.allow_retrieve)

    def test_make_it(self):
        sot = quota.Quota(**EXAMPLE)
        self.assertEqual(EXAMPLE['load_balancer'], sot.load_balancers)
        self.assertEqual(EXAMPLE['listener'], sot.listeners)
        self.assertEqual(EXAMPLE['pool'], sot.pools)
        self.assertEqual(EXAMPLE['health_monitor'], sot.health_monitors)
        self.assertEqual(EXAMPLE['member'], sot.members)
        self.assertEqual(EXAMPLE['project_id'], sot.project_id)
