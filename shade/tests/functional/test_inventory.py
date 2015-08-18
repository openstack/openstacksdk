# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
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

"""
test_inventory
----------------------------------

Functional tests for `shade` inventory methods.
"""

from shade import openstack_cloud
from shade import inventory

from shade.tests import base
from shade.tests.functional.util import pick_flavor, pick_image


class TestInventory(base.TestCase):
    def setUp(self):
        super(TestInventory, self).setUp()
        # This needs to use an admin account, otherwise a public IP
        # is not allocated from devstack.
        self.cloud = openstack_cloud(cloud='devstack-admin')
        self.inventory = inventory.OpenStackInventory()
        self.server_name = 'test_inventory_server'
        self.nova = self.cloud.nova_client
        self.flavor = pick_flavor(self.nova.flavors.list())
        if self.flavor is None:
            self.assertTrue(False, 'no sensible flavor available')
        self.image = pick_image(self.nova.images.list())
        if self.image is None:
            self.assertTrue(False, 'no sensible image available')
        self.addCleanup(self._cleanup_servers)
        self.cloud.create_server(
            name=self.server_name, image=self.image, flavor=self.flavor,
            wait=True, auto_ip=True)

    def _cleanup_servers(self):
        for i in self.nova.servers.list():
            if i.name.startswith(self.server_name):
                self.nova.servers.delete(i)

    def _test_host_content(self, host):
        self.assertEquals(host['image']['id'], self.image.id)
        self.assertNotIn('links', host['image'])
        self.assertEquals(host['flavor']['id'], self.flavor.id)
        self.assertNotIn('links', host['flavor'])
        self.assertNotIn('links', host)
        self.assertIsInstance(host['volumes'], list)
        self.assertIsInstance(host['metadata'], dict)
        self.assertIn('interface_ip', host)

    def test_get_host(self):
        host = self.inventory.get_host(self.server_name)
        self.assertIsNotNone(host)
        self.assertEquals(host['name'], self.server_name)
        self._test_host_content(host)
        host_found = False
        for host in self.inventory.list_hosts():
            if host['name'] == self.server_name:
                host_found = True
                self._test_host_content(host)
        self.assertTrue(host_found)
