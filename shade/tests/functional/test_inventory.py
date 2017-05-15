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

from shade import inventory

from shade.tests.functional import base
from shade.tests.functional.util import pick_flavor


class TestInventory(base.BaseFunctionalTestCase):
    def setUp(self):
        super(TestInventory, self).setUp()
        # This needs to use an admin account, otherwise a public IP
        # is not allocated from devstack.
        self.inventory = inventory.OpenStackInventory()
        self.server_name = self.getUniqueString('inventory')
        self.flavor = pick_flavor(
            self.user_cloud.list_flavors(get_extra=False))
        if self.flavor is None:
            self.assertTrue(False, 'no sensible flavor available')
        self.image = self.pick_image()
        self.addCleanup(self._cleanup_server)
        server = self.operator_cloud.create_server(
            name=self.server_name, image=self.image, flavor=self.flavor,
            wait=True, auto_ip=True)
        self.server_id = server['id']

    def _cleanup_server(self):
        self.user_cloud.delete_server(self.server_id, wait=True)

    def _test_host_content(self, host):
        self.assertEqual(host['image']['id'], self.image.id)
        self.assertNotIn('links', host['image'])
        self.assertEqual(host['flavor']['id'], self.flavor.id)
        self.assertNotIn('links', host['flavor'])
        self.assertNotIn('links', host)
        self.assertIsInstance(host['volumes'], list)
        self.assertIsInstance(host['metadata'], dict)
        self.assertIn('interface_ip', host)

    def _test_expanded_host_content(self, host):
        self.assertEqual(host['image']['name'], self.image.name)
        self.assertEqual(host['flavor']['name'], self.flavor.name)

    def test_get_host(self):
        host = self.inventory.get_host(self.server_id)
        self.assertIsNotNone(host)
        self.assertEqual(host['name'], self.server_name)
        self._test_host_content(host)
        self._test_expanded_host_content(host)
        host_found = False
        for host in self.inventory.list_hosts():
            if host['id'] == self.server_id:
                host_found = True
                self._test_host_content(host)
        self.assertTrue(host_found)

    def test_get_host_no_detail(self):
        host = self.inventory.get_host(self.server_id, expand=False)
        self.assertIsNotNone(host)
        self.assertEqual(host['name'], self.server_name)

        self.assertEqual(host['image']['id'], self.image.id)
        self.assertNotIn('links', host['image'])
        self.assertNotIn('name', host['name'])
        self.assertEqual(host['flavor']['id'], self.flavor.id)
        self.assertNotIn('links', host['flavor'])
        self.assertNotIn('name', host['flavor'])

        host_found = False
        for host in self.inventory.list_hosts(expand=False):
            if host['id'] == self.server_id:
                host_found = True
                self._test_host_content(host)
        self.assertTrue(host_found)
