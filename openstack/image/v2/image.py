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

from openstack.image import image_service
from openstack import resource


class Image(resource.Resource):
    resources_key = 'images'
    base_path = '/images'
    service = image_service.ImageService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True

    # Properties
    checksum = resource.prop('checksum')
    container_format = resource.prop('container_format')
    created_at = resource.prop('created_at')
    disk_format = resource.prop('disk_format')
    min_disk = resource.prop('min_disk')
    name = resource.prop('name')
    owner = resource.prop('owner')
    properties = resource.prop('properties')
    protected = resource.prop('protected', type=bool)
    status = resource.prop('status')
    tags = resource.prop('tags')
    updated_at = resource.prop('updated_at')
    virtual_size = resource.prop('virtual_size')
    visibility = resource.prop('visibility')