# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
#
# See the License for the specific language governing permissions and
# limitations under the License.

"""
test_port
----------------------------------

Functional tests for `shade` port resource.
"""

import string
import random

from shade import openstack_cloud
from shade.exc import OpenStackCloudException
from shade.tests import base


class TestPort(base.TestCase):

    def setUp(self):
        super(TestPort, self).setUp()
        self.cloud = openstack_cloud(cloud='devstack-admin')
        # Skip Neutron tests if neutron is not present
        if not self.cloud.has_service('network'):
            self.skipTest('Network service not supported by cloud')

        # Generate a unique port name to allow concurrent tests
        self.new_port_name = 'test_' + ''.join(
            random.choice(string.ascii_lowercase) for _ in range(5))

        self.addCleanup(self._cleanup_ports)

    def _cleanup_ports(self):
        exception_list = list()

        for p in self.cloud.list_ports():
            if p['name'].startswith(self.new_port_name):
                try:
                    self.cloud.delete_port(name_or_id=p['id'])
                except Exception as e:
                    # We were unable to delete this port, let's try with next
                    exception_list.append(str(e))
                    continue

        if exception_list:
            # Raise an error: we must make users aware that something went
            # wrong
            raise OpenStackCloudException('\n'.join(exception_list))

    def test_create_port(self):
        port_name = self.new_port_name + '_create'

        networks = self.cloud.list_networks()
        if not networks:
            self.assertFalse('no sensible network available')

        port = self.cloud.create_port(
            network_id=networks[0]['id'], name=port_name)
        self.assertIsInstance(port, dict)
        self.assertTrue('id' in port)
        self.assertEqual(port.get('name'), port_name)

    def test_get_port(self):
        port_name = self.new_port_name + '_get'

        networks = self.cloud.list_networks()
        if not networks:
            self.assertFalse('no sensible network available')

        port = self.cloud.create_port(
            network_id=networks[0]['id'], name=port_name)
        self.assertIsInstance(port, dict)
        self.assertTrue('id' in port)
        self.assertEqual(port.get('name'), port_name)

        updated_port = self.cloud.get_port(name_or_id=port['id'])
        # extra_dhcp_opts is added later by Neutron...
        if 'extra_dhcp_opts' in updated_port:
            del updated_port['extra_dhcp_opts']
        self.assertEqual(port, updated_port)

    def test_update_port(self):
        port_name = self.new_port_name + '_update'
        new_port_name = port_name + '_new'

        networks = self.cloud.list_networks()
        if not networks:
            self.assertFalse('no sensible network available')

        self.cloud.create_port(
            network_id=networks[0]['id'], name=port_name)

        port = self.cloud.update_port(name_or_id=port_name,
                                      name=new_port_name)
        self.assertIsInstance(port, dict)
        self.assertEqual(port.get('name'), new_port_name)

        updated_port = self.cloud.get_port(name_or_id=port['id'])
        self.assertEqual(port.get('name'), new_port_name)
        self.assertEqual(port, updated_port)

    def test_delete_port(self):
        port_name = self.new_port_name + '_delete'

        networks = self.cloud.list_networks()
        if not networks:
            self.assertFalse('no sensible network available')

        port = self.cloud.create_port(
            network_id=networks[0]['id'], name=port_name)
        self.assertIsInstance(port, dict)
        self.assertTrue('id' in port)
        self.assertEqual(port.get('name'), port_name)

        updated_port = self.cloud.get_port(name_or_id=port['id'])
        self.assertIsNotNone(updated_port)

        self.cloud.delete_port(name_or_id=port_name)

        updated_port = self.cloud.get_port(name_or_id=port['id'])
        self.assertIsNone(updated_port)
