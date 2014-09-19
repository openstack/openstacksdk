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


class User(resource.Resource):
    resource_key = 'user'
    resources_key = 'users'
    base_path = '/users'
    service = identity_service.IdentityService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True

    # Properties
    default_project_id = resource.prop('default_project_id')
    description = resource.prop('description')
    domain_id = resource.prop('domain_id')
    email = resource.prop('email')
    enabled = resource.prop('enabled', type=bool)
    name = resource.prop('name')
    password = resource.prop('password')
