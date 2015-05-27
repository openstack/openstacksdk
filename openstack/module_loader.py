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


def load_service_plugins(namespace):
    service_plugins = extension.ExtensionManager(
        namespace=namespace,
        invoke_on_load=True,
    )
    services = {}
    for service in service_plugins:
        service = service.obj
        service.interface = None
        services[service.service_type] = service
    return services
