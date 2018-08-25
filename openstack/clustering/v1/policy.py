# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from openstack import resource


class Policy(resource.Resource):
    resource_key = 'policy'
    resources_key = 'policies'
    base_path = '/policies'

    # Capabilities
    allow_list = True
    allow_fetch = True
    allow_create = True
    allow_delete = True
    allow_commit = True

    commit_method = 'PATCH'

    _query_mapping = resource.QueryParameters(
        'name', 'type', 'sort', 'global_project')

    # Properties
    #: The name of the policy.
    name = resource.Body('name')
    #: The type name of the policy.
    type = resource.Body('type')
    #: The ID of the project this policy belongs to.
    project_id = resource.Body('project')
    # The domain ID of the policy.
    domain_id = resource.Body('domain')
    #: The ID of the user who created this policy.
    user_id = resource.Body('user')
    #: The timestamp when the policy is created.
    created_at = resource.Body('created_at')
    #: The timestamp when the policy was last updated.
    updated_at = resource.Body('updated_at')
    #: The specification of the policy.
    spec = resource.Body('spec', type=dict)
    #: A dictionary containing runtime data of the policy.
    data = resource.Body('data', type=dict)


class PolicyValidate(Policy):
    base_path = '/policies/validate'

    # Capabilities
    allow_list = False
    allow_fetch = False
    allow_create = True
    allow_delete = False
    allow_commit = False

    commit_method = 'PUT'
