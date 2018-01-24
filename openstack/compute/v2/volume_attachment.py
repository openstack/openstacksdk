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


class VolumeAttachment(resource.Resource):
    resource_key = 'volumeAttachment'
    resources_key = 'volumeAttachments'
    base_path = '/servers/%(server_id)s/os-volume_attachments'
    service = compute_service.ComputeService()

    # capabilities
    allow_create = True
    allow_get = True
    allow_update = False
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters("limit", "offset")

    #: Name of the device such as, /dev/vdb.
    device = resource.Body('device')
    #: The ID of the attachment.
    id = resource.Body('id')
    #: The ID for the server.
    server_id = resource.URI('server_id')
    #: The ID of the attached volume.
    volume_id = resource.Body('volumeId')
    #: The ID of the attachment you want to delete or update.
    attachment_id = resource.Body('attachment_id', alternate_id=True)
