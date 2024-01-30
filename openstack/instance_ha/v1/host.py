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

from openstack import resource


class Host(resource.Resource):
    resource_key = "host"
    resources_key = "hosts"
    base_path = "/segments/%(segment_id)s/hosts"

    # capabilities
    # 1] GET /v1/segments/<segment_uuid>/hosts
    # 2] GET /v1/segments/<segment_uuid>/hosts/<host_uuid>
    # 3] POST /v1/segments/<segment_uuid>/hosts
    # 4] PUT /v1/segments/<segment_uuid>/hosts
    # 5] DELETE /v1/segments/<segment_uuid>/hosts
    allow_list = True
    allow_fetch = True
    allow_create = True
    allow_commit = True
    allow_delete = True

    #: A Uuid of representing this host
    uuid = resource.Body("uuid")
    #: A failover segment ID of this host(in URI)
    segment_id = resource.URI("segment_id")
    #: A created time of this host
    created_at = resource.Body("created_at")
    #: A latest updated time of this host
    updated_at = resource.Body("updated_at")
    #: A name of this host
    name = resource.Body("name")
    #: A type of this host
    type = resource.Body("type")
    #: A control attributes of this host
    control_attributes = resource.Body("control_attributes")
    #: A maintenance status of this host
    on_maintenance = resource.Body("on_maintenance")
    #: A reservation status of this host
    reserved = resource.Body("reserved")
    #: A failover segment ID of this host(in Body)
    failover_segment_id = resource.Body("failover_segment_id")

    _query_mapping = resource.QueryParameters(
        "sort_key",
        "sort_dir",
        failover_segment_id="failover_segment_id",
        type="type",
        on_maintenance="on_maintenance",
        reserved="reserved",
    )
