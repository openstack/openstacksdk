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

from openstack import format
from openstack import resource


class Role(resource.Resource):
    resource_key = 'role'
    resources_key = 'roles'
    base_path = '/OS-KSADM/roles'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    # Properties
    #: The description of the role. *Type: string*
    description = resource.Body('description')
    #: Setting this attribute to ``False`` prevents this role from being
    #: available in the role list. *Type: bool*
    is_enabled = resource.Body('enabled', type=format.BoolStr)
    #: Unique role name. *Type: string*
    name = resource.Body('name')
