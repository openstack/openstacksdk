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

from openstack.network.v2 import ndp_proxy
from openstack.tests.unit import base

EXAMPLE = {
    'id': 'np_id',
    'name': 'np_name',
    'router_id': 'router-uuid',
    'port_id': 'port-uuid',
    'project_id': 'project-uuid',
    'description': 'fake-desc',
    'created_at': '2021-12-21T19:14:57.233772',
    'updated_at': '2021-12-21T19:14:57.233772',
}


class TestNDPProxy(base.TestCase):
    def test_basic(self):
        sot = ndp_proxy.NDPProxy()
        self.assertEqual('ndp_proxy', sot.resource_key)
        self.assertEqual('ndp_proxies', sot.resources_key)
        self.assertEqual('/ndp_proxies', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = ndp_proxy.NDPProxy(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['router_id'], sot.router_id)
        self.assertEqual(EXAMPLE['port_id'], sot.port_id)
        self.assertEqual(EXAMPLE['project_id'], sot.project_id)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['created_at'], sot.created_at)
        self.assertEqual(EXAMPLE['updated_at'], sot.updated_at)
