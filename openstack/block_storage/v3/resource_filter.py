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


class ResourceFilter(resource.Resource):
    """Resource Filter"""

    resources_key = "resource_filters"
    base_path = "/resource_filters"

    _query_mapping = resource.QueryParameters(
        'resource',
        include_pagination_defaults=False,
    )

    # Capabilities
    allow_list = True

    # resource_filters introduced in 3.33
    _max_microversion = '3.33'

    #: Properties
    #: The list of filters that are applicable to the specified resource.
    filters = resource.Body('filters', type=list)
    #: The resource that the filters will be applied to.
    resource = resource.Body('resource', type=str)
