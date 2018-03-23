# Copyright(c) 2018 Nippon Telegraph and Telephone Corporation
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

from openstack.instance_ha import instance_ha_service
from openstack import resource


class Segment(resource.Resource):
    resource_key = "segment"
    resources_key = "segments"
    base_path = "/segments"
    service = instance_ha_service.InstanceHaService()

    # capabilities
    # 1] GET /v1/segments
    # 2] GET /v1/segments/<segment_uuid>
    # 3] POST /v1/segments
    # 4] PUT /v1/segments/<segment_uuid>
    # 5] DELETE /v1/segments/<segment_uuid>
    allow_list = True
    allow_get = True
    allow_create = True
    allow_update = True
    allow_delete = True

    # Properties
    # Refer "https://github.com/openstack/masakari/tree/
    # master/masakari/api/openstack/ha/schemas"
    # for properties of each API

    #: A ID of representing this segment.
    id = resource.Body("id")
    #: A Uuid of representing this segment.
    uuid = resource.Body("uuid")
    #: A created time of representing this segment.
    created_at = resource.Body("created_at")
    #: A latest updated time of representing this segment.
    updated_at = resource.Body("updated_at")
    #: The name of this segment.
    name = resource.Body("name")
    #: The description of this segment.
    description = resource.Body("description")
    #: The recovery method of this segment.
    recovery_method = resource.Body("recovery_method")
    #: The service type of this segment.
    service_type = resource.Body("service_type")

    _query_mapping = resource.QueryParameters(
        "sort_key", "sort_dir", recovery_method="recovery_method",
        service_type="service_type")
