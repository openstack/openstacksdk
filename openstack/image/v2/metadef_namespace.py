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


# TODO(schwicke): create and delete still need to be implemented
class MetadefNamespace(resource.Resource):
    resources_key = 'namespaces'
    base_path = '/metadefs/namespaces'

    allow_fetch = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        "limit",
        "marker",
        "resource_types",
        "sort_dir",
        "sort_key",
        "visibility"
    )
    created_at = resource.Body('created_at')
    description = resource.Body('description')
    display_name = resource.Body('display_name')
    is_protected = resource.Body('protected', type=bool)
    namespace = resource.Body('namespace')
    owner = resource.Body('owner')
    resource_type_associations = resource.Body('resource_type_associations',
                                               type=list,
                                               list_type=dict)
    visibility = resource.Body('visibility')
