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
from openstack.common import metadata
from openstack import resource


class Image(resource.Resource, metadata.MetadataMixin):
    resource_key = 'image'
    resources_key = 'images'
    base_path = '/images'

    # capabilities
    allow_fetch = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        "server",
        "name",
        "status",
        "type",
        min_disk="minDisk",
        min_ram="minRam",
        changes_since="changes-since",
    )

    # Properties
    #: Links pertaining to this image. This is a list of dictionaries,
    #: each including keys ``href`` and ``rel``, and optionally ``type``.
    links = resource.Body('links')
    #: The name of this image.
    name = resource.Body('name')
    #: Timestamp when the image was created.
    created_at = resource.Body('created')
    #: The mimimum disk size. *Type: int*
    min_disk = resource.Body('minDisk', type=int)
    #: The minimum RAM size. *Type: int*
    min_ram = resource.Body('minRam', type=int)
    #: If this image is still building, its progress is represented here.
    #: Once an image is created, progres will be 100. *Type: int*
    progress = resource.Body('progress', type=int)
    #: The status of this image.
    status = resource.Body('status')
    #: Timestamp when the image was updated.
    updated_at = resource.Body('updated')
    #: Size of the image in bytes. *Type: int*
    size = resource.Body('OS-EXT-IMG-SIZE:size', type=int)


ImageDetail = Image
