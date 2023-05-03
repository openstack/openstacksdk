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


class VpnEndpointGroup(resource.Resource):
    resource_key = 'endpoint_group'
    resources_key = 'endpoint_groups'
    base_path = '/vpn/endpoint-groups'

    _allow_unknown_attrs_in_body = True

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
        type='endpoint_type',
    )

    # Properties
    #: Human-readable description for the resource.
    description = resource.Body('description')
    #: List of endpoints of the same type, for the endpoint group.
    #: The values will depend on type.
    endpoints = resource.Body('endpoints', type=list)
    #: Human-readable name of the resource. Default is an empty string.
    name = resource.Body('name')
    project_id = resource.Body('project_id', alias='tenant_id')
    #: Tenant_id (deprecated attribute).
    tenant_id = resource.Body('tenant_id', deprecated=True)
    #: The type of the endpoints in the group. A valid value is subnet, cidr,
    #: network, router, or vlan. Only subnet and cidr are supported at this
    #: moment.
    type = resource.Body('type')
