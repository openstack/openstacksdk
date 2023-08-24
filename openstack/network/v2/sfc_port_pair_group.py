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


class SfcPortPairGroup(resource.Resource):
    resource_key = 'port_pair_group'
    resources_key = 'port_pair_groups'
    base_path = '/sfc/port_pair_groups'

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
    )

    # Properties
    #: Human-readable description for the resource.
    description = resource.Body('description')
    #: Human-readable name of the resource. Default is an empty string.
    name = resource.Body('name')
    #: List of port-pair UUIDs.
    port_pairs = resource.Body('port_pairs', type=list)
    #: Dictionary of port pair group parameters, in the form of
    #: lb_fields: list of regex (eth|ip|tcp|udp)_(src|dst)),
    #: ppg_n_tuple_mapping: ingress_n_tuple or egress_n_tuple.
    #: The ingress or egress tuple is a dict with the following keys:
    #: source_ip_prefix, destination_ip_prefix, source_port_range_min,
    #: source_port_range_max, destination_port_range_min,
    #: destination_port_range_max.
    port_pair_group_parameters = resource.Body(
        'port_pair_group_parameters', type=dict
    )
    #: True if passive Tap service functions support is enabled,
    #: default is False.
    is_tap_enabled = resource.Body('tap_enabled', type=bool)
    project_id = resource.Body('project_id', alias='tenant_id')
    #: Tenant_id (deprecated attribute).
    tenant_id = resource.Body('tenant_id', deprecated=True)
