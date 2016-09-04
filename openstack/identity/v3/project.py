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
from openstack import resource2 as resource


class Project(resource.Resource):
    resource_key = 'project'
    resources_key = 'projects'
    base_path = '/projects'
    service = identity_service.IdentityService()

    # capabilities
    allow_create = True
    allow_get = True
    allow_update = True
    allow_delete = True
    allow_list = True
    patch_update = True

    # Properties
    #: The description of the project. *Type: string*
    description = resource.Body('description')
    #: References the domain ID which owns the project; if a domain ID is not
    #: specified by the client, the Identity service implementation will
    #: default it to the domain ID to which the client's token is scoped.
    #: *Type: string*
    domain_id = resource.Body('domain_id')
    #: Indicates whether the project also acts as a domain. If set to True,
    #: the project acts as both a project and a domain. Default is False.
    #: New in version 3.6
    is_domain = resource.Body('is_domain', type=bool)
    #: Setting this attribute to ``False`` prevents users from authorizing
    #: against this project. Additionally, all pre-existing tokens authorized
    #: for the project are immediately invalidated. Re-enabling a project
    #: does not re-enable pre-existing tokens. *Type: bool*
    is_enabled = resource.Body('enabled', type=bool)
    #: Unique project name, within the owning domain. *Type: string*
    name = resource.Body('name')
    #: The ID of the parent of the project.
    #: New in version 3.4
    parent_id = resource.Body('parent_id')
