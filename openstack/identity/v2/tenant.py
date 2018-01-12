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


class Tenant(resource.Resource):
    resource_key = 'tenant'
    resources_key = 'tenants'
    base_path = '/tenants'
    service = identity_service.AdminService()

    # capabilities
    allow_create = True
    allow_get = True
    allow_update = True
    allow_delete = True
    allow_list = True

    # Properties
    #: The description of the tenant. *Type: string*
    description = resource.Body('description')
    #: Setting this attribute to ``False`` prevents users from authorizing
    #: against this tenant. Additionally, all pre-existing tokens authorized
    #: for the tenant are immediately invalidated. Re-enabling a tenant
    #: does not re-enable pre-existing tokens. *Type: bool*
    is_enabled = resource.Body('enabled', type=bool)
    #: Unique tenant name. *Type: string*
    name = resource.Body('name')
