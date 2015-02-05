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


class Port(resource.Resource):
    resource_key = 'port'
    resources_key = 'ports'
    base_path = '/ports'
    service = network_service.NetworkService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True
    put_update = True

    # Properties
    admin_state_up = resource.prop('admin_state_up', type=bool)
    allowed_address_pairs = resource.prop('allowed_address_pairs', type=dict)
    binding_host_id = resource.prop('binding:host_id')
    binding_profile = resource.prop('binding:profile')
    binding_vif_details = resource.prop('binding:vif_details', type=dict)
    binding_vif_type = resource.prop('binding:vif_type')
    binding_vnic_type = resource.prop('binding:vnic_type')
    device_id = resource.prop('device_id')
    device_owner = resource.prop('device_owner')
    extra_dhcp_opts = resource.prop('extra_dhcp_opts', type=dict)
    fixed_ips = resource.prop('fixed_ips')
    mac_address = resource.prop('mac_address')
    name = resource.prop('name')
    network_id = resource.prop('network_id')
    project_id = resource.prop('tenant_id')
    security_groups = resource.prop('security_groups')
    status = resource.prop('status')
