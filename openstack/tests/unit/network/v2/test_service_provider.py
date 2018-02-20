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

from openstack.tests.unit import base

from openstack.network.v2 import service_provider

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'service_type': 'L3_ROUTER_NAT',
    'name': '4',
    'default': False,
}


class TestServiceProvider(base.TestCase):

    def test_basic(self):
        sot = service_provider.ServiceProvider()

        self.assertEqual('service_providers', sot.resources_key)
        self.assertEqual('/service-providers', sot.base_path)
        self.assertEqual('network', sot.service.service_type)
        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.allow_get)
        self.assertFalse(sot.allow_update)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = service_provider.ServiceProvider(**EXAMPLE)
        self.assertEqual(EXAMPLE['service_type'], sot.service_type)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['default'], sot.is_default)
