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


class Listener(resource.Resource):
    resource_key = 'listener'
    resources_key = 'listeners'
    base_path = '/listeners'
    service = network_service.NetworkService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True
    put_update = True

    # Properties
    connection_limit = resource.prop('connection_limit')
    default_pool_id = resource.prop('default_pool_id')
    description = resource.prop('description')
    load_balancer_id = resource.prop('load_balancer_id')
    name = resource.prop('name')
    project_id = resource.prop('tenant_id')
    protocol = resource.prop('protocol')
    protocol_port = resource.prop('protocol_port')
