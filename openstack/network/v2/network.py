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


class Network(resource.Resource):
    resource_key = 'network'
    resources_key = 'networks'
    base_path = '/networks'
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
    name = resource.prop('name')
    project_id = resource.prop('tenant_id')
    provider_network_type = resource.prop('provider:network_type')
    provider_physical_network = resource.prop('provider:physical_network')
    provider_segmentation_id = resource.prop('provider:segmentation_id')
    router_external = resource.prop('router:external')
    segments = resource.prop('segments')
    shared = resource.prop('shared', type=bool)
    status = resource.prop('status')
    subnets = resource.prop('subnets')
