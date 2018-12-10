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


class PortForwarding(resource.Resource):
    name_attribute = "floating_ip_port_forwarding"
    resource_name = "port forwarding"
    resource_key = 'port_forwarding'
    resources_key = 'port_forwardings'
    base_path = '/floatingips/%(floatingip_id)s/port_forwardings'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'internal_port_id', 'external_port', 'protocol'
    )

    # Properties
    #: The ID of Floating IP address
    floatingip_id = resource.URI('floatingip_id')
    #: The ID of internal port
    internal_port_id = resource.Body('internal_port_id')
    #: The internal IP address
    internal_ip_address = resource.Body('internal_ip_address')
    #: The internal TCP/UDP/other port number
    internal_port = resource.Body('internal_port', type=int)
    #: The external TCP/UDP/other port number
    external_port = resource.Body('external_port', type=int)
    #: The protocol
    protocol = resource.Body('protocol')
