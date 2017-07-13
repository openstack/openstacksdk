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
from openstack.map_reduce import map_reduce_service
from openstack import resource2 as resource


class DataSource(resource.Resource):
    resource_key = "data_source"
    resources_key = "data_sources"
    base_path = "/data-sources"
    service = map_reduce_service.MapReduceService()

    # capabilities
    allow_create = True
    allow_update = True
    allow_list = True
    allow_get = True
    allow_delete = True

    _query_mapping = resource.QueryParameters(
        "sort_by"
    )

    #: Properties
    #: Data Source name
    name = resource.Body("name")
    #: Data Source Type, supports: ``hdfs``, ``obs``, ``swift``
    type = resource.Body("type")
    #: Data Source url, if type is HDFS, url should like */data-source-path*,
    #: if type is obs, url should like *s3a://data-source-path*
    url = resource.Body("url")
    #: Data source description
    description = resource.Body("description")
    #: Reserved attribute, is data-source protected
    is_protected = resource.Body("is_protected", type=bool)
    #: Reserved attribute, is data-source public
    is_public = resource.Body("is_public", type=bool)
    #: UTC date and time of the data-source created time
    created_at = resource.Body("created_at")
    #: UTC date and time of the data-source last updated time
    updated_at = resource.Body("updated_at")
    #: The tenant this data-source belongs to
    tenant_id = resource.Body("tenant_id")
