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

from openstack import format
from openstack.image import image_service
from openstack import resource


class Image(resource.Resource):
    resource_key = 'image'
    resources_key = 'images'
    base_path = '/images'
    service = image_service.ImageService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True

    #: Hash of the image data used. The Image service uses this value
    #: for verification.
    checksum = resource.prop('checksum')
    #: The container format refers to whether the VM image is in a file
    #: format that also contains metadata about the actual VM.
    #: Container formats include OVF and Amazon AMI. In addition,
    #: a VM image might not have a container format - instead,
    #: the image is just a blob of unstructured data.
    container_format = resource.prop('container_format')
    #: A URL to copy an image from
    copy_from = resource.prop('copy_from')
    #: The timestamp when this image was created.
    #: *Type: datetime object parsed from ISO 8601 formatted string*
    created_at = resource.prop('created_at', type=format.ISO8601)
    #: Valid values are: aki, ari, ami, raw, iso, vhd, vdi, qcow2, or vmdk.
    #: The disk format of a VM image is the format of the underlying
    #: disk image. Virtual appliance vendors have different formats for
    #: laying out the information contained in a VM disk image.
    disk_format = resource.prop('disk_format')
    #: Defines whether the image can be deleted.
    #: *Type: bool*
    is_protected = resource.prop('protected', type=bool)
    #: ``True`` if this is a public image.
    #: *Type: bool*
    is_public = resource.prop('is_public', type=bool)
    #: A location for the image identified by a URI
    location = resource.prop('location')
    #: The minimum disk size in GB that is required to boot the image.
    min_disk = resource.prop('min_disk')
    #: The minimum amount of RAM in MB that is required to boot the image.
    min_ram = resource.prop('min_ram')
    #: Name for the image. Note that the name of an image is not unique
    #: to a Glance node. The API cannot expect users to know the names
    #: of images owned by others.
    name = resource.prop('name')
    #: The ID of the owner, or project, of the image.
    owner_id = resource.prop('owner')
    #: Properties, if any, that are associated with the image.
    properties = resource.prop('properties')
    #: The size of the image data, in bytes.
    size = resource.prop('size')
    #: The image status.
    status = resource.prop('status')
    #: The timestamp when this image was last updated.
    #: *Type: datetime object parsed from ISO 8601 formatted string*
    updated_at = resource.prop('updated_at', type=format.ISO8601)
