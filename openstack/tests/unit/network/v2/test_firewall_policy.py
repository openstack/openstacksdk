# Copyright (c) 2018 China Telecom Corporation
# All Rights Reserved.
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

import testtools

from openstack.network.v2 import firewall_policy


EXAMPLE = {
    'description': '1',
    'name': '2',
    'firewall_rules': [
        'a30b0ec2-a468-4b1c-8dbf-928ded2a57a8',
        '8d562e98-24f3-46e1-bbf3-d9347c0a67ee',
    ],
    'shared': True,
    'project_id': '4',
}


class TestFirewallPolicy(testtools.TestCase):
    def test_basic(self):
        sot = firewall_policy.FirewallPolicy()
        self.assertEqual('firewall_policy', sot.resource_key)
        self.assertEqual('firewall_policies', sot.resources_key)
        self.assertEqual('/fwaas/firewall_policies', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = firewall_policy.FirewallPolicy(**EXAMPLE)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['firewall_rules'], sot.firewall_rules)
        self.assertEqual(EXAMPLE['shared'], sot.shared)
        self.assertEqual(list, type(sot.firewall_rules))
        self.assertEqual(EXAMPLE['project_id'], sot.project_id)
