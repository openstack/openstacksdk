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

from openstack.network.v2 import firewall_rule

EXAMPLE = {
    'action': 'allow',
    'description': '1',
    'destination_ip_address': '10.0.0.2/24',
    'destination_port': '2',
    'name': '3',
    'enabled': True,
    'ip_version': 4,
    'protocol': 'tcp',
    'shared': True,
    'source_ip_address': '10.0.1.2/24',
    'source_port': '5',
    'project_id': '6',
}


class TestFirewallRule(testtools.TestCase):

    def test_basic(self):
        sot = firewall_rule.FirewallRule()
        self.assertEqual('firewall_rule', sot.resource_key)
        self.assertEqual('firewall_rules', sot.resources_key)
        self.assertEqual('/fwaas/firewall_rules', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = firewall_rule.FirewallRule(**EXAMPLE)
        self.assertEqual(EXAMPLE['action'], sot.action)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['destination_ip_address'],
                         sot.destination_ip_address)
        self.assertEqual(EXAMPLE['destination_port'], sot.destination_port)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['enabled'], sot.enabled)
        self.assertEqual(EXAMPLE['ip_version'], sot.ip_version)
        self.assertEqual(EXAMPLE['protocol'], sot.protocol)
        self.assertEqual(EXAMPLE['shared'], sot.shared)
        self.assertEqual(EXAMPLE['source_ip_address'],
                         sot.source_ip_address)
        self.assertEqual(EXAMPLE['source_port'], sot.source_port)
        self.assertEqual(EXAMPLE['project_id'], sot.project_id)
