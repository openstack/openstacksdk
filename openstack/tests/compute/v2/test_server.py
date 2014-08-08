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

from openstack.compute.v2 import server

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'accessIPv4': '1',
    'accessIPv6': '2',
    'addresses': {'region': '3'},
    'created': '4',
    'flavor': {'id': '5'},
    'hostId': '6',
    'id': IDENTIFIER,
    'image': {'id': '8'},
    'links': '9',
    'metadata': '10',
    'name': '11',
    'progress': 12,
    'tenant_id': '13',
    'status': '14',
    'updated': '15',
    'user_id': '16',
}


class TestServer(testtools.TestCase):

    def test_basic(self):
        sot = server.Server()
        self.assertEqual('server', sot.resource_key)
        self.assertEqual('servers', sot.resources_key)
        self.assertEqual('/servers', sot.base_path)
        self.assertEqual('compute', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = server.Server(EXAMPLE)
        self.assertEqual(EXAMPLE['accessIPv4'], sot.access_ipv4)
        self.assertEqual(EXAMPLE['accessIPv6'], sot.access_ipv6)
        self.assertEqual(EXAMPLE['addresses'], sot.addresses)
        self.assertEqual(EXAMPLE['created'], sot.created)
        self.assertEqual(EXAMPLE['flavor'], sot.flavor)
        self.assertEqual(EXAMPLE['hostId'], sot.host_id)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['image'], sot.image)
        self.assertEqual(EXAMPLE['links'], sot.links)
        self.assertEqual(EXAMPLE['metadata'], sot.metadata)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['progress'], sot.progress)
        self.assertEqual(EXAMPLE['tenant_id'], sot.project_id)
        self.assertEqual(EXAMPLE['status'], sot.status)
        self.assertEqual(EXAMPLE['updated'], sot.updated)
        self.assertEqual(EXAMPLE['user_id'], sot.user_id)
