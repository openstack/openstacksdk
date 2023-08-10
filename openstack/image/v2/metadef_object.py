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


class MetadefObject(resource.Resource):
    resources_key = 'objects'
    base_path = '/metadefs/namespaces/%(namespace_name)s/objects'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        "visibility",
        "resource_types",
        "sort_key",
        "sort_dir",
    )

    created_at = resource.Body('created_at')
    description = resource.Body('description')
    name = resource.Body('name', alternate_id=True)
    namespace_name = resource.URI('namespace_name')
    properties = resource.Body('properties')
    required = resource.Body('required')
    updated_at = resource.Body('updated_at')
