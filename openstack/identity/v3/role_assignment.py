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

from openstack.identity import identity_service
from openstack import resource


class RoleAssignment(resource.Resource):
    resource_key = 'role_assignment'
    resources_key = 'role_assignments'
    base_path = '/role_assignments'
    service = identity_service.IdentityService()

    # capabilities
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'group_id', 'role_id', 'scope_domain_id', 'scope_project_id',
        'user_id', 'effective', 'include_names', 'include_subtree'
    )

    # Properties
    #: The links for the service resource.
    links = resource.Body('links')
    #: The role (dictionary contains only id) *Type: dict*
    role = resource.Body('role', type=dict)
    #: The scope (either domain or group dictionary contains id) *Type: dict*
    scope = resource.Body('scope', type=dict)
    #: The user (dictionary contains only id) *Type: dict*
    user = resource.Body('user', type=dict)
    #: The group (dictionary contains only id) *Type: dict*
    group = resource.Body('group', type=dict)
