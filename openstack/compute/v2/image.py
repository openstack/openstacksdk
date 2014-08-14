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


class Image(resource.Resource):
    resource_key = 'image'
    resources_key = 'images'
    base_path = '/images'
    service = compute_service.ComputeService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True

    # Properties
    created = resource.prop('created')
    links = resource.prop('links')
    metadata = resource.prop('metadata', type=dict)
    min_disk = resource.prop('minDisk', type=int)
    min_ram = resource.prop('minRam', type=int)
    name = resource.prop('name')
    progress = resource.prop('progress', type=int)
    status = resource.prop('status')
    updated = resource.prop('updated')
