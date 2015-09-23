# -*- coding: utf-8 -*-

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

"""
test_network
----------------------------------

Functional tests for `shade` network methods.
"""

import random
import string

from shade import openstack_cloud
from shade.exc import OpenStackCloudException
from shade.tests import base


class TestNetwork(base.TestCase):
    def setUp(self):
        super(TestNetwork, self).setUp()
        self.cloud = openstack_cloud(cloud='devstack-admin')
        if not self.cloud.has_service('network'):
            self.skipTest('Network service not supported by cloud')
        self.network_prefix = 'test_network' + ''.join(
            random.choice(string.ascii_lowercase) for _ in range(5))
        self.addCleanup(self._cleanup_networks)

    def _cleanup_networks(self):
        exception_list = list()
        for network in self.cloud.list_networks():
            if network['name'].startswith(self.network_prefix):
                try:
                    self.cloud.delete_network(network['name'])
                except Exception as e:
                    exception_list.append(str(e))
                    continue

        if exception_list:
            raise OpenStackCloudException('\n'.join(exception_list))

    def test_create_network_basic(self):
        net1_name = self.network_prefix + '_net1'
        net1 = self.cloud.create_network(name=net1_name)
        self.assertIn('id', net1)
        self.assertEqual(net1_name, net1['name'])
        self.assertFalse(net1['shared'])
        self.assertFalse(net1['router:external'])
        self.assertTrue(net1['admin_state_up'])

    def test_create_network_advanced(self):
        net1_name = self.network_prefix + '_net1'
        net1 = self.cloud.create_network(
            name=net1_name,
            shared=True,
            external=True,
            admin_state_up=False,
        )
        self.assertIn('id', net1)
        self.assertEqual(net1_name, net1['name'])
        self.assertTrue(net1['router:external'])
        self.assertTrue(net1['shared'])
        self.assertFalse(net1['admin_state_up'])
