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


class Server(resource.Resource):
    resource_key = 'server'
    resources_key = 'servers'
    base_path = '/servers'
    service = compute_service.ComputeService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True

    # Properties
    access_ipv4 = resource.prop('accessIPv4')
    access_ipv6 = resource.prop('accessIPv6')
    addresses = resource.prop('addresses', type=dict)
    created = resource.prop('created')
    flavor = resource.prop('flavor', type=dict)
    host_id = resource.prop('hostId')
    image = resource.prop('image', type=dict)
    links = resource.prop('links')
    metadata = resource.prop('metadata')
    name = resource.prop('name')
    progress = resource.prop('progress', type=int)
    project_id = resource.prop('tenant_id')
    status = resource.prop('status')
    updated = resource.prop('updated')
    user_id = resource.prop('user_id')
