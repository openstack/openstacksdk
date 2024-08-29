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
from openstack.common import tag
from openstack import resource


class L7Policy(resource.Resource, tag.TagMixin):
    resource_key = 'l7policy'
    resources_key = 'l7policies'
    base_path = '/lbaas/l7policies'

    # capabilities
    allow_create = True
    allow_list = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True

    _query_mapping = resource.QueryParameters(
        'action',
        'description',
        'listener_id',
        'name',
        'position',
        'redirect_pool_id',
        'redirect_url',
        'provisioning_status',
        'operating_status',
        'redirect_prefix',
        'project_id',
        is_admin_state_up='admin_state_up',
        **tag.TagMixin._tag_query_parameters,
    )

    #: Properties
    #: The action to be taken l7policy is matched
    action = resource.Body('action')
    #: Timestamp when the L7 policy was created.
    created_at = resource.Body('created_at')
    #: The l7policy description
    description = resource.Body('description')
    #: The administrative state of the l7policy *Type: bool*
    is_admin_state_up = resource.Body('admin_state_up', type=bool)
    #: The ID of the listener associated with this l7policy
    listener_id = resource.Body('listener_id')
    #: The l7policy name
    name = resource.Body('name')
    #: Operating status of the member.
    operating_status = resource.Body('operating_status')
    #: Sequence number of this l7policy
    position = resource.Body('position', type=int)
    #: The ID of the project this l7policy is associated with.
    project_id = resource.Body('project_id')
    #: The provisioning status of this l7policy
    provisioning_status = resource.Body('provisioning_status')
    #: The ID of the pool to which the requests will be redirected
    redirect_pool_id = resource.Body('redirect_pool_id')
    #: The URL prefix to which the requests should be redirected
    redirect_prefix = resource.Body('redirect_prefix')
    #: The URL to which the requests should be redirected
    redirect_url = resource.Body('redirect_url')
    #: The list of L7Rules associated with the l7policy
    rules = resource.Body('rules', type=list)
    #: Timestamp when the member was last updated.
    updated_at = resource.Body('updated_at')
