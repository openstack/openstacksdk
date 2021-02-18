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


class ServerInterface(resource.Resource):
    resource_key = 'interfaceAttachment'
    resources_key = 'interfaceAttachments'
    base_path = '/servers/%(server_id)s/os-interface'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = False
    allow_delete = True
    allow_list = True

    #: Fixed IP addresses with subnet IDs.
    fixed_ips = resource.Body('fixed_ips')
    #: The MAC address.
    mac_addr = resource.Body('mac_addr')
    #: The network ID.
    net_id = resource.Body('net_id')
    #: The ID of the port for which you want to create an interface.
    port_id = resource.Body('port_id', alternate_id=True)
    #: The port state.
    port_state = resource.Body('port_state')
    #: The ID for the server.
    server_id = resource.URI('server_id')
    #: Tags for the virtual interfaces.
    tag = resource.Body('tag')
    # tag introduced in 2.70
    _max_microversion = '2.70'
