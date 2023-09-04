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


class DefaultSecurityGroupRule(_base.NetworkResource):
    resource_key = 'default_security_group_rule'
    resources_key = 'default_security_group_rules'
    base_path = '/default-security-group-rules'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = False
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'id',
        'description',
        'remote_group_id',
        'remote_address_group_id',
        'direction',
        'protocol',
        'port_range_min',
        'port_range_max',
        'remote_ip_prefix',
        'used_in_default_sg',
        'used_in_non_default_sg',
        'sort_dir',
        'sort_key',
        ether_type='ethertype',
    )

    # Properties
    #: The default security group rule description.
    description = resource.Body('description')
    #: The remote security group ID to be associated with this security
    #: group rule created from this template.
    #: You can specify either ``remote_group_id`` or #:
    #: ``remote_address_group_id`` or ``remote_ip_prefix``.
    remote_group_id = resource.Body('remote_group_id')
    #: The remote address group ID to be associated with this security
    #: group rule created from that template.
    #: You can specify either ``remote_group_id`` or
    #: ``remote_address_group_id`` or ``remote_ip_prefix``.
    remote_address_group_id = resource.Body('remote_address_group_id')
    #: ``ingress`` or ``egress``: The direction in which the security group #:
    #: rule will be applied. See 'direction' field in the security group rule
    #: API.
    direction = resource.Body('direction')
    #: The protocol that is matched by the security group rule.
    #: Valid values are ``null``, ``tcp``, ``udp``, and ``icmp``.
    protocol = resource.Body('protocol')
    #: The minimum port number in the range that is matched by the
    #: security group rule. If the protocol is TCP or UDP, this value
    #: must be less than or equal to the value of the port_range_max
    #: attribute. If the protocol is ICMP, this value must be an ICMP type.
    port_range_min = resource.Body('port_range_min', type=int)
    #: The maximum port number in the range that is matched by the
    #: security group rule. The port_range_min attribute constrains
    #: the port_range_max attribute. If the protocol is ICMP, this
    #: value must be an ICMP type.
    port_range_max = resource.Body('port_range_max', type=int)
    #: The remote IP prefix to be associated with this security group rule.
    #: You can specify either ``remote_group_id`` or
    #: ``remote_address_group_id`` or ``remote_ip_prefix``.
    #: This attribute matches the specified IP prefix as the source or
    #: destination IP address of the IP packet depending on direction.
    remote_ip_prefix = resource.Body('remote_ip_prefix')
    #: Must be IPv4 or IPv6, and addresses represented in CIDR must match
    #: the ingress or egress rules.
    ether_type = resource.Body('ethertype')
    #: Indicate if this template be used to create security group rules in the
    #: default security group created automatically for each project.
    used_in_default_sg = resource.Body('used_in_default_sg', type=bool)
    #: Indicate if this template be used to create security group rules in the
    #: custom security groups created in the project by users.
    used_in_non_default_sg = resource.Body('used_in_non_default_sg', type=bool)
