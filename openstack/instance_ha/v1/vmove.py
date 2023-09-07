# Copyright(c) 2022 Inspur
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from openstack import resource


class VMove(resource.Resource):
    resource_key = "vmove"
    resources_key = "vmoves"
    base_path = "/notifications/%(notification_id)s/vmoves"

    # capabilities
    # 1] GET /v1/notifications/{notification_uuid}/vmoves
    # 2] GET /v1/notifications/{notification_uuid}/vmoves/{vmove_uuid}
    allow_list = True
    allow_fetch = True

    _query_mapping = resource.QueryParameters(
        "sort_key",
        "sort_dir",
        "type",
        "status",
    )

    #: A ID of representing this vmove
    id = resource.Body("id")
    #: A UUID of representing this vmove
    uuid = resource.Body("uuid")
    #: The notification UUID this vmove belongs to(in URI)
    notification_id = resource.URI("notification_id")
    #: A created time of this vmove
    created_at = resource.Body("created_at")
    #: A latest updated time of this vmove
    updated_at = resource.Body("updated_at")
    #: The instance uuid of this vmove
    server_id = resource.Body("instance_uuid")
    #: The instance name of this vmove
    server_name = resource.Body("instance_name")
    #: The source host of this vmove
    source_host = resource.Body("source_host")
    #: The dest host of this vmove
    dest_host = resource.Body("dest_host")
    #: A start time of this vmove
    start_time = resource.Body("start_time")
    #: A end time of this vmove
    end_time = resource.Body("end_time")
    #: The status of this vmove
    status = resource.Body("status")
    #: The type of this vmove
    type = resource.Body("type")
    #: The message of this vmove
    message = resource.Body("message")
