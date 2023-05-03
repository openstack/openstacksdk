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


class NDPProxy(resource.Resource):
    resource_name = "ndp proxy"
    resource_key = 'ndp_proxy'
    resources_key = 'ndp_proxies'
    base_path = '/ndp_proxies'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    _allow_unknown_attrs_in_body = True

    _query_mapping = resource.QueryParameters(
        "sort_key",
        "sort_dir",
        'name',
        'description',
        'project_id',
        'router_id',
        'port_id',
        'ip_address',
    )

    # Properties
    #: Timestamp at which the NDP proxy was created.
    created_at = resource.Body('created_at')
    #: The description
    description = resource.Body('description')
    #: The ID of the NDP proxy.
    id = resource.Body('id')
    #: The internal IP address
    ip_address = resource.Body('ip_address')
    # The name of ndp proxy
    name = resource.Body('name')
    #: The ID of internal port
    port_id = resource.Body('port_id')
    #: The ID of the project that owns the NDP proxy.
    project_id = resource.Body('project_id')
    #: The NDP proxy revision number.
    revision_number = resource.Body('revision_number')
    #: The ID of Router
    router_id = resource.Body('router_id')
    #: Timestamp at which the NDP proxy was last updated.
    updated_at = resource.Body('updated_at')
