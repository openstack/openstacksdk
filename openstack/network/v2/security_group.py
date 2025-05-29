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


class SecurityGroup(_base.NetworkResource, _base.TagMixinNetwork):
    resource_key = 'security_group'
    resources_key = 'security_groups'
    base_path = '/security-groups'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'description',
        'fields',
        'id',
        'name',
        'stateful',
        'project_id',
        'tenant_id',
        'revision_number',
        'sort_dir',
        'sort_key',
        is_shared='shared',
        **_base.TagMixinNetwork._tag_query_parameters,
    )

    # Properties
    #: Timestamp when the security group was created.
    created_at = resource.Body('created_at')
    #: The security group description.
    description = resource.Body('description')
    #: The security group name.
    name = resource.Body('name')
    #: Whether the security group is stateful or not.
    stateful = resource.Body('stateful')
    #: The ID of the project this security group is associated with.
    project_id = resource.Body('project_id')
    #: A list of
    #: :class:`~openstack.network.v2.security_group_rule.SecurityGroupRule`
    #: objects. *Type: list*
    security_group_rules = resource.Body('security_group_rules', type=list)
    #: The ID of the project this security group is associated with.
    tenant_id = resource.Body('tenant_id', deprecated=True)
    #: Timestamp when the security group was last updated.
    updated_at = resource.Body('updated_at')
    #: Indicates whether this Security Group is shared across all projects.
    #: *Type: bool*
    is_shared = resource.Body('shared', type=bool)
