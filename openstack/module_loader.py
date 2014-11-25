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
Load various modules for authorization and services.
"""
from stevedore import extension

from openstack import exceptions


class ModuleLoader(object):

    def __init__(self):
        self.auth_mgr = extension.ExtensionManager(
            namespace="openstack.auth.plugin",
            invoke_on_load=False,
        )

    def get_auth_plugin(self, plugin_name):
        if not plugin_name:
            plugin_name = 'identity'
        try:
            return self.auth_mgr[plugin_name].plugin
        except KeyError:
            msg = ('Could not find authorization plugin <%s>' % plugin_name)
            raise exceptions.NoMatchingPlugin(msg)

    def list_auth_plugins(self):
        return self.auth_mgr.names()
