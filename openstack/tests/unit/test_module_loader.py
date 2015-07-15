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

from openstack import exceptions
from openstack import module_loader
from openstack.tests.unit import base


class TestModuleLoader(base.TestCase):
    def test_load_identity_v2(self):
        loader = module_loader.ModuleLoader()
        plugin = loader.get_auth_plugin('v2password')
        self.assertEqual('openstack.auth.identity.v2', str(plugin.__module__))
        plugin = loader.get_auth_plugin('v2token')
        self.assertEqual('openstack.auth.identity.v2', str(plugin.__module__))

    def test_load_identity_v3(self):
        loader = module_loader.ModuleLoader()
        plugin = loader.get_auth_plugin('v3password')
        self.assertEqual('openstack.auth.identity.v3', str(plugin.__module__))
        plugin = loader.get_auth_plugin('v3token')
        self.assertEqual('openstack.auth.identity.v3', str(plugin.__module__))

    def test_load_identity_discoverable(self):
        plugin = module_loader.ModuleLoader().get_auth_plugin('password')
        self.assertEqual('openstack.auth.identity.discoverable',
                         str(plugin.__module__))

    def test_load_none(self):
        plugin = module_loader.ModuleLoader().get_auth_plugin(None)
        self.assertEqual('openstack.auth.identity.discoverable',
                         str(plugin.__module__))

    def test_load_empty(self):
        plugin = module_loader.ModuleLoader().get_auth_plugin('')
        self.assertEqual('openstack.auth.identity.discoverable',
                         str(plugin.__module__))

    def test_load_bogus(self):
        self.assertRaises(exceptions.NoMatchingPlugin,
                          module_loader.ModuleLoader().get_auth_plugin, 'wot')

    def test_list_auth_plugins(self):
        plugins = sorted(module_loader.ModuleLoader().list_auth_plugins())
        expected = ['password', 'token', 'v2password', 'v2token',
                    'v3password', 'v3token']
        self.assertEqual(expected, plugins)
