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


class Role(resource.Resource):
    resource_key = 'role'
    resources_key = 'roles'
    base_path = '/roles'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True
    commit_method = 'PATCH'

    _query_mapping = resource.QueryParameters(
        'name', 'domain_id')

    # Properties
    #: Unique role name, within the owning domain. *Type: string*
    name = resource.Body('name')
    #: User-facing description of the role. *Type: string*
    description = resource.Body('description')
    #: References the domain ID which owns the role. *Type: string*
    domain_id = resource.Body('domain_id')
    #: The links for the service resource.
    links = resource.Body('links')
