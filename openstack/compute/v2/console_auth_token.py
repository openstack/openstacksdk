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

from openstack import resource


class ConsoleAuthToken(resource.Resource):
    resource_key = 'console'
    base_path = '/os-console-auth-tokens'

    # capabilities
    allow_fetch = True

    _max_microversion = '2.99'

    # Properties
    #: Instance UUID
    instance_uuid = resource.Body('instance_uuid')
    #: Hypervisor host
    host = resource.Body('host')
    #: Hypervisor port
    port = resource.Body('port')
    #: Hypervisor TLS port
    tls_port = resource.Body('tls_port')
    #: Internal access path
    internal_access_path = resource.Body('internal_access_path')
