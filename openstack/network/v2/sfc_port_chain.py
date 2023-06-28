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


class SfcPortChain(resource.Resource):
    resource_key = 'port_chain'
    resources_key = 'port_chains'
    base_path = '/sfc/port_chains'

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
    #: List of port-pair-group UUIDs.
    port_pair_groups = resource.Body('port_pair_groups', type=list)
    #: List of flow-classifier UUIDs.
    flow_classifiers = resource.Body('flow_classifiers', type=list)
    #: A dictionary of chain parameters, correlation values can be
    #: mpls and nsh, symmetric can be True or False.
    chain_parameters = resource.Body('chain_parameters', type=dict)
    project_id = resource.Body('project_id', alias='tenant_id')
    #: Tenant_id (deprecated attribute).
    tenant_id = resource.Body('tenant_id', deprecated=True)
