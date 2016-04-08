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

from openstack.network import network_service
from openstack import resource


class SecurityGroupRule(resource.Resource):
    resource_key = 'security_group_rule'
    resources_key = 'security_group_rules'
    base_path = '/security-group-rules'
    service = network_service.NetworkService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = False
    allow_delete = True
    allow_list = True

    # Properties
    #: ``ingress`` or ``egress``: The direction in which the security group
    #: rule is applied. For a compute instance, an ingress security group
    #: rule is applied to incoming ingress traffic for that instance.
    #: An egress rule is applied to traffic leaving the instance.
    direction = resource.prop('direction')
    #: The security group rule description.
    description = resource.prop('description')
    #: Must be IPv4 or IPv6, and addresses represented in CIDR must match
    #: the ingress or egress rules.
    ethertype = resource.prop('ethertype')
    #: The maximum port number in the range that is matched by the
    #: security group rule. The port_range_min attribute constrains
    #: the port_range_max attribute. If the protocol is ICMP, this
    #: value must be an ICMP type.
    port_range_max = resource.prop('port_range_max')
    #: The minimum port number in the range that is matched by the
    #: security group rule. If the protocol is TCP or UDP, this value
    #: must be less than or equal to the value of the port_range_max
    #: attribute. If the protocol is ICMP, this value must be an ICMP type.
    port_range_min = resource.prop('port_range_min')
    #: The ID of the project this security group rule is associated with.
    project_id = resource.prop('tenant_id')
    #: The protocol that is matched by the security group rule.
    #: Valid values are ``null``, ``tcp``, ``udp``, and ``icmp``.
    protocol = resource.prop('protocol')
    #: The remote security group ID to be associated with this security
    #: group rule. You can specify either ``remote_group_id`` or
    #: ``remote_ip_prefix`` in the request body.
    remote_group_id = resource.prop('remote_group_id')
    #: The remote IP prefix to be associated with this security group rule.
    #: You can specify either ``remote_group_id`` or ``remote_ip_prefix``
    #: in the request body. This attribute matches the specified IP prefix
    #: as the source IP address of the IP packet.
    remote_ip_prefix = resource.prop('remote_ip_prefix')
    #: The security group ID to associate with this security group rule.
    security_group_id = resource.prop('security_group_id')
