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

from openstack.network import network_service
from openstack import resource2 as resource


class AddressScope(resource.Resource):
    """Address scope extension."""
    resource_key = 'address_scope'
    resources_key = 'address_scopes'
    base_path = '/address-scopes'
    service = network_service.NetworkService()

    # capabilities
    allow_create = True
    allow_get = True
    allow_update = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'name', 'ip_version',
        project_id='tenant_id',
        is_shared='shared',
    )

    # Properties
    #: The address scope name.
    name = resource.Body('name')
    #: The ID of the project that owns the address scope.
    project_id = resource.Body('tenant_id')
    #: The IP address family of the address scope.
    #: *Type: int*
    ip_version = resource.Body('ip_version', type=int)
    #: Indicates whether this address scope is shared across all projects.
    #: *Type: bool*
    is_shared = resource.Body('shared', type=bool)
