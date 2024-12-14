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


class SecurityGroupRule(_base.NetworkResource, _base.TagMixinNetwork):
    resource_key = 'security_group_rule'
    resources_key = 'security_group_rules'
    base_path = '/security-group-rules'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = False
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'description',
        'direction',
        'id',
        'protocol',
        'remote_group_id',
        'security_group_id',
        'remote_address_group_id',
        'port_range_max',
        'port_range_min',
        'remote_ip_prefix',
        'revision_number',
        'project_id',
        'tenant_id',
        'sort_dir',
        'sort_key',
        ether_type='ethertype',
        **_base.TagMixinNetwork._tag_query_parameters,
    )

    # Properties
    #: Timestamp when the security group rule was created.
    created_at = resource.Body('created_at')
    #: The security group rule description.
    description = resource.Body('description')
    #: ``ingress`` or ``egress``: The direction in which the security group
    #: rule is applied. For a compute instance, an ingress security group
    #: rule is applied to incoming ingress traffic for that instance.
    #: An egress rule is applied to traffic leaving the instance.
    direction = resource.Body('direction')
    #: Must be IPv4 or IPv6, and addresses represented in CIDR must match
    #: the ingress or egress rules.
    ether_type = resource.Body('ethertype')
    #: The maximum port number in the range that is matched by the
    #: security group rule. The port_range_min attribute constrains
    #: the port_range_max attribute. If the protocol is ICMP, this
    #: value must be an ICMP type.
    port_range_max = resource.Body('port_range_max', type=int)
    #: The minimum port number in the range that is matched by the
    #: security group rule. If the protocol is TCP or UDP, this value
    #: must be less than or equal to the value of the port_range_max
    #: attribute. If the protocol is ICMP, this value must be an ICMP type.
    port_range_min = resource.Body('port_range_min', type=int)
    #: The ID of the project this security group rule is associated with.
    project_id = resource.Body('project_id')
    #: The protocol that is matched by the security group rule.
    #: Valid values are ``null``, ``tcp``, ``udp``, and ``icmp``.
    protocol = resource.Body('protocol')
    #: The remote security group ID to be associated with this security
    #: group rule. You can specify either ``remote_group_id`` or
    #: ``remote_address_group_id`` or ``remote_ip_prefix``.
    remote_group_id = resource.Body('remote_group_id')
    #: The remote address group ID to be associated with this security
    #: group rule. You can specify either ``remote_group_id`` or
    #: ``remote_address_group_id`` or ``remote_ip_prefix``.
    remote_address_group_id = resource.Body('remote_address_group_id')
    #: The remote IP prefix to be associated with this security group rule.
    #: You can specify either ``remote_group_id`` or
    #: ``remote_address_group_id`` or ``remote_ip_prefix``.
    #: This attribute matches the specified IP prefix as the source or
    #: destination IP address of the IP packet depending on direction.
    remote_ip_prefix = resource.Body('remote_ip_prefix')
    #: The security group ID to associate with this security group rule.
    security_group_id = resource.Body('security_group_id')
    #: The ID of the project this security group rule is associated with.
    tenant_id = resource.Body('tenant_id', deprecated=True)
    #: Timestamp when the security group rule was last updated.
    updated_at = resource.Body('updated_at')

    def _prepare_request(self, *args, **kwargs):
        _request = super()._prepare_request(*args, **kwargs)
        # Old versions of Neutron do not handle being passed a
        # remote_address_group_id and raise and error.  Remove it from
        # the body if it is blank.
        if not self.remote_address_group_id:
            if 'security_group_rule' in _request.body:
                _rule = _request.body['security_group_rule']
                _rule.pop('remote_address_group_id', None)
        return _request
