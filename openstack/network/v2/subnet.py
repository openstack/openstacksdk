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

from openstack import format
from openstack.network import network_service
from openstack import resource


class Subnet(resource.Resource):
    resource_key = 'subnet'
    resources_key = 'subnets'
    base_path = '/subnets'
    service = network_service.NetworkService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True

    # Properties
    #: The start and end addresses for the allocation pools.
    allocation_pools = resource.prop('allocation_pools')
    #: The CIDR.
    cidr = resource.prop('cidr')
    #: Timestamp when the subnet was created.
    #: *Type: datetime object parsed from ISO 8601 formatted string*
    created_at = resource.prop('created_at', type=format.ISO8601)
    #: The subnet description.
    description = resource.prop('description')
    #: A list of DNS nameservers.
    dns_nameservers = resource.prop('dns_nameservers')
    #: The gateway IP address.
    gateway_ip = resource.prop('gateway_ip')
    #: A list of host routes.
    host_routes = resource.prop('host_routes')
    #: The IP version, which is ``4`` or ``6``.
    ip_version = resource.prop('ip_version')
    #: The IPv6 address modes which are 'dhcpv6-stateful', 'dhcpv6-stateless',
    #: or 'SLAAC'
    ipv6_address_mode = resource.prop('ipv6_address_mode')
    #: The IPv6 router advertisements modes
    ipv6_ra_mode = resource.prop('ipv6_ra_mode')
    #: Set to ``True`` if DHCP is enabled and ``False`` if DHCP is disabled.
    #: *Type: bool*
    is_dhcp_enabled = resource.prop('enable_dhcp', type=bool)
    #: The subnet name.
    name = resource.prop('name')
    #: The ID of the attached network.
    network_id = resource.prop('network_id')
    #: The ID of the project this subnet is associated with.
    project_id = resource.prop('tenant_id')
    #: The subnet pool ID from which to obtain a CIDR.
    subnet_pool_id = resource.prop('subnetpool_id')
    #: Timestamp when the subnet was last updated.
    #: *Type: datetime object parsed from ISO 8601 formatted string*
    updated_at = resource.prop('updated_at', type=format.ISO8601)
