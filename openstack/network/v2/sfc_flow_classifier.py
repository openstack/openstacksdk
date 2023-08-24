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


class SfcFlowClassifier(resource.Resource):
    resource_key = 'flow_classifier'
    resources_key = 'flow_classifiers'
    base_path = '/sfc/flow_classifiers'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'description',
        'name',
        'project_id',
        'tenant_id',
        'ethertype',
        'protocol',
        'source_port_range_min',
        'source_port_range_max',
        'destination_port_range_min',
        'destination_port_range_max',
        'logical_source_port',
        'logical_destination_port',
    )

    # Properties
    #: Human-readable description for the resource.
    description = resource.Body('description')
    #: Human-readable name of the resource. Default is an empty string.
    name = resource.Body('name')
    #: Must be IPv4 or IPv6, and addresses represented in CIDR must match
    # the ingress or egress rules.
    ethertype = resource.Body('ethertype')
    #: The IP protocol can be represented by a string, an integer, or null.
    #: Valid values: any (0), ah (51), dccp (33), egp (8), esp (50), gre (47),
    #: icmp (1), icmpv6 (58), igmp (2), ipip (4), ipv6-encap (41),
    #: ipv6-frag (44), ipv6-icmp (58), ipv6-nonxt (59), ipv6-opts (60),
    #: ipv6-route (43), ospf (89), pgm (113), rsvp (46), sctp (132), tcp (6),
    #: udp (17), udplite (136), vrrp (112).
    protocol = resource.Body('protocol')
    #: Minimum source protocol port.
    source_port_range_min = resource.Body('source_port_range_min', type=int)
    #: Maximum source protocol port.
    source_port_range_max = resource.Body('source_port_range_max', type=int)
    #: Minimum destination protocol port.
    destination_port_range_min = resource.Body(
        'destination_port_range_min', type=int
    )
    #: Maximum destination protocol port.
    destination_port_range_max = resource.Body(
        'destination_port_range_max', type=int
    )
    #: The source IP prefix.
    source_ip_prefix = resource.Body('source_ip_prefix')
    #: The destination IP prefix.
    destination_ip_prefix = resource.Body('destination_ip_prefix')
    #: The UUID of the source logical port.
    logical_source_port = resource.Body('logical_source_port')
    #: The UUID of the destination logical port.
    logical_destination_port = resource.Body('logical_destination_port')
    #: A dictionary of L7 parameters, in the form of
    #: logical_source_network: uuid, logical_destination_network: uuid.
    l7_parameters = resource.Body('l7_parameters', type=dict)
    #: Summary field of a Flow Classifier, composed of the
    #: protocol, source protcol port, destination ptocolo port,
    #: logical_source_port, logical_destination_port and
    #: l7_parameters
    summary = resource.Computed('summary', default='')
    project_id = resource.Body('project_id', alias='tenant_id')
    #: Tenant_id (deprecated attribute).
    tenant_id = resource.Body('tenant_id', deprecated=True)
