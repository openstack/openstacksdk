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
from openstack.tests import base


class TestModuleLoader(base.TestCase):
    def test_load_identity_v2(self):
        plugin = module_loader.ModuleLoader().get_auth_plugin('identity_v2')
        self.assertEqual('openstack.auth.identity.v2', str(plugin.__module__))

    def test_load_identity_v3(self):
        plugin = module_loader.ModuleLoader().get_auth_plugin('identity_v3')
        self.assertEqual('openstack.auth.identity.v3', str(plugin.__module__))

    def test_load_identity_discoverable(self):
        plugin = module_loader.ModuleLoader().get_auth_plugin('identity')
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
        self.assertEqual(['identity', 'identity_v2', 'identity_v3'], plugins)
