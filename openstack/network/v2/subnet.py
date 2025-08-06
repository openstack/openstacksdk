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

from openstack.network.v2 import _base
from openstack import resource


class Subnet(_base.NetworkResource, _base.TagMixinNetwork):
    resource_key = 'subnet'
    resources_key = 'subnets'
    base_path = '/subnets'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    # NOTE: Query on list or datetime fields are currently not supported.
    _query_mapping = resource.QueryParameters(
        'cidr',
        'description',
        'gateway_ip',
        'id',
        'ip_version',
        'ipv6_address_mode',
        'ipv6_ra_mode',
        'name',
        'network_id',
        'segment_id',
        'dns_publish_fixed_ip',
        'project_id',
        'sort_key',
        'sort_dir',
        is_dhcp_enabled='enable_dhcp',
        subnet_pool_id='subnetpool_id',
        use_default_subnet_pool='use_default_subnetpool',
        **_base.TagMixinNetwork._tag_query_parameters,
    )

    # Properties
    #: List of allocation pools each of which has a start and an end address
    #: for this subnet
    allocation_pools = resource.Body('allocation_pools', type=list)
    #: The CIDR.
    cidr = resource.Body('cidr')
    #: Timestamp when the subnet was created.
    created_at = resource.Body('created_at')
    #: The subnet description.
    description = resource.Body('description')
    #: A list of DNS nameservers.
    dns_nameservers = resource.Body('dns_nameservers', type=list)
    #: Whether to publish DNS records for fixed IPs
    dns_publish_fixed_ip = resource.Body('dns_publish_fixed_ip', type=bool)
    #: The gateway IP address.
    gateway_ip = resource.Body('gateway_ip')
    #: A list of host routes.
    host_routes = resource.Body('host_routes', type=list)
    #: The IP version, which is 4 or 6.
    #: *Type: int*
    ip_version = resource.Body('ip_version', type=int)
    #: The IPv6 address modes which are 'dhcpv6-stateful', 'dhcpv6-stateless'
    #: or 'slaac'.
    ipv6_address_mode = resource.Body('ipv6_address_mode')
    #: The IPv6 router advertisements modes which can be 'slaac',
    #: 'dhcpv6-stateful', 'dhcpv6-stateless'.
    ipv6_ra_mode = resource.Body('ipv6_ra_mode')
    #: Set to ``True`` if DHCP is enabled and ``False`` if DHCP is disabled.
    #: *Type: bool*
    is_dhcp_enabled = resource.Body('enable_dhcp', type=bool)
    #: The subnet name.
    name = resource.Body('name')
    #: The ID of the attached network.
    network_id = resource.Body('network_id')
    #: The prefix length to use for subnet allocation from a subnet pool
    prefix_length = resource.Body('prefixlen')
    #: The ID of the project this subnet is associated with.
    project_id = resource.Body('project_id', alias='tenant_id')
    #: Tenant_id (deprecated attribute).
    tenant_id = resource.Body('tenant_id', deprecated=True)
    #: The ID of the segment this subnet is associated with.
    segment_id = resource.Body('segment_id')
    #: Service types for this subnet
    service_types = resource.Body('service_types', type=list)
    #: The subnet pool ID from which to obtain a CIDR.
    subnet_pool_id = resource.Body('subnetpool_id')
    #: Timestamp when the subnet was last updated.
    updated_at = resource.Body('updated_at')
    #: Whether to use the default subnet pool to obtain a CIDR.
    use_default_subnet_pool = resource.Body(
        'use_default_subnetpool', type=bool
    )
