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

from openstack import resource


class QoSSpec(resource.Resource):
    resource_key = "qos_specs"
    resources_key = "qos_specs"
    base_path = "/qos-specs"

    _query_mapping = resource.QueryParameters(
        "project_id",
        "limit",
        "marker",
        "offset",
        "sort_dir",
        "sort_key",
        "sort",
    )

    # capabilities
    allow_fetch = True
    allow_create = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    # Properties
    consumer = resource.Body("consumer")
    id = resource.Body("id", type=str)
    name = resource.Body("name")
    specs = resource.Body("specs")
