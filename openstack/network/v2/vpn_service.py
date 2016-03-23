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
from openstack import resource


class VPNService(resource.Resource):
    resource_key = 'vpnservice'
    resources_key = 'vpnservices'
    base_path = '/vpn/vpnservices'
    service = network_service.NetworkService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True

    # Properties
    #: Human-readable description for the vpnservice.
    description = resource.prop('description')
    #: The unique ID for the vpnservice.
    id = resource.prop('id')
    #: The administrative state of the vpnservice, which is up ``True`` or
    #: down ``False``. *Type: bool*
    is_admin_state_up = resource.prop('admin_state_up', type=bool)
    #: The vpnservice name.
    name = resource.prop('name')
    #: ID of the router into which the VPN service is inserted.
    router_id = resource.prop('router_id')
    #: The ID of the project this vpnservice is associated with.
    project_id = resource.prop('tenant_id')
    #: The vpnservice status.
    status = resource.prop('status')
    #: The ID of the subnet on which the tenant wants the vpnservice.
    subnet_id = resource.prop('subnet_id')
