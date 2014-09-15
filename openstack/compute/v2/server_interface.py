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

from openstack.compute import compute_service
from openstack import resource


class ServerInterface(resource.Resource):
    id_attribute = 'mac_addr'
    resource_key = 'interfaceAttachment'
    resources_key = 'interfaceAttachments'
    base_path = '/servers/%(server_id)s/os-interface'
    service = compute_service.ComputeService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = False
    allow_delete = True
    allow_list = True

    # Properties
    fixed_ips = resource.prop('fixed_ips')
    mac_addr = resource.prop('mac_addr')
    net_id = resource.prop('net_id')
    port_id = resource.prop('port_id')
    port_state = resource.prop('port_state')
    server_id = resource.prop('server_id')
