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


class Flavor(resource.Resource):
    resource_key = 'flavor'
    resources_key = 'flavors'
    base_path = '/flavors'
    service = compute_service.ComputeService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True

    # Properties
    disk = resource.prop('disk', type=int)
    is_public = resource.prop('os-flavor-access:is_public', type=bool)
    links = resource.prop('links')
    name = resource.prop('name')
    ram = resource.prop('ram', type=int)
    vcpus = resource.prop('vcpus', type=int)
