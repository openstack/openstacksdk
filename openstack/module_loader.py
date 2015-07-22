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
Load various modules for authorization and eventually services.
"""
from stevedore import extension

from openstack import exceptions


def load_service_extensions(namespace):
    service_extensions = extension.ExtensionManager(
        namespace=namespace,
        invoke_on_load=True,
    )
    services = {}
    for service in service_extensions:
        service = service.obj
        service.set_visibility(None)
        services[service.service_type] = service
    return services


class ModuleLoader(object):

    def __init__(self):
        """Create a module loader."""
        self.auth_mgr = extension.ExtensionManager(
            namespace="openstack.auth.plugin",
            invoke_on_load=False,
        )

    def get_auth_plugin(self, plugin_name):
        """Get an authentication plugin by name."""
        if not plugin_name:
            plugin_name = 'password'
        try:
            return self.auth_mgr[plugin_name].plugin
        except KeyError:
            msg = ('Could not find authorization plugin <%s>' % plugin_name)
            raise exceptions.NoMatchingPlugin(msg)

    def list_auth_plugins(self):
        """Get a list of all the authentication plugins."""
        return self.auth_mgr.names()
