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
from openstack.compute.v2 import metadata
from openstack import format
from openstack import resource


class Image(resource.Resource, metadata.MetadataMixin):
    resource_key = 'image'
    resources_key = 'images'
    base_path = '/images'
    service = compute_service.ComputeService()

    # capabilities
    allow_retrieve = True
    allow_delete = True
    allow_list = True

    # Properties
    #: Links pertaining to this image. This is a list of dictionaries,
    #: each including keys ``href`` and ``rel``, and optionally ``type``.
    links = resource.prop('links')
    #: The name of this image.
    name = resource.prop('name')
    #: Timestamp when the image was created.
    #: *Type: datetime object parsed from ISO 8601 formatted string*
    created_at = resource.prop('created', type=format.ISO8601)
    #: Metadata pertaining to this image. *Type: dict*
    metadata = resource.prop('metadata', type=dict)
    #: The mimimum disk size. *Type: int*
    min_disk = resource.prop('minDisk', type=int)
    #: The minimum RAM size. *Type: int*
    min_ram = resource.prop('minRam', type=int)
    #: If this image is still building, its progress is represented here.
    #: Once an image is created, progres will be 100. *Type: int*
    progress = resource.prop('progress', type=int)
    #: The status of this image.
    status = resource.prop('status')
    #: Timestamp when the image was updated.
    #: *Type: datetime object parsed from ISO 8601 formatted string*
    updated_at = resource.prop('updated', type=format.ISO8601)
    #: Size of the image in bytes. *Type: int*
    size = resource.prop('OS-EXT-IMG-SIZE:size', type=int)


class ImageDetail(Image):
    base_path = '/images/detail'

    allow_retrieve = False
    allow_delete = False
    allow_list = True
