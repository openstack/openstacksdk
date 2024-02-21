#   Copyright 2021 Huawei, Inc. All rights reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

from openstack import resource


class LocalIP(resource.Resource):
    """Local IP extension."""

    resource_name = "local ip"
    resource_key = "local_ip"
    resources_key = "local_ips"
    base_path = "/local_ips"

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    _allow_unknown_attrs_in_body = True

    _query_mapping = resource.QueryParameters(
        'sort_key',
        'sort_dir',
        'name',
        'description',
        'project_id',
        'network_id',
        'local_port_id',
        'local_ip_address',
        'ip_mode',
    )

    # Properties
    #: Timestamp at which the floating IP was created.
    created_at = resource.Body('created_at')
    #: The local ip description.
    description = resource.Body('description')
    #: The ID of the local ip.
    id = resource.Body('id')
    #: The local ip ip-mode.
    ip_mode = resource.Body('ip_mode')
    #: The Local IP address.
    local_ip_address = resource.Body('local_ip_address')
    #: The ID of the port that owns the local ip.
    local_port_id = resource.Body('local_port_id')
    #: The local ip name.
    name = resource.Body('name')
    #: The ID of the network that owns the local ip.
    network_id = resource.Body('network_id')
    #: The ID of the project that owns the local ip.
    project_id = resource.Body('project_id')
    #: The local ip revision number.
    revision_number = resource.Body('revision_number')
    #: Timestamp at which the floating IP was last updated.
    updated_at = resource.Body('updated_at')
