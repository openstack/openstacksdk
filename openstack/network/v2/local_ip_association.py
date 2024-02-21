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


class LocalIPAssociation(resource.Resource):
    """Local IP extension."""

    resource_key = "port_association"
    resources_key = "port_associations"
    base_path = "/local_ips/%(local_ip_id)s/port_associations"

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    _allow_unknown_attrs_in_body = True

    _query_mapping = resource.QueryParameters(
        'fixed_port_id',
        'fixed_ip',
        'host',
        'sort_key',
        'sort_dir',
    )

    # Properties
    #: The fixed port ID.
    fixed_port_id = resource.Body('fixed_port_id')
    #: The fixed IP.
    fixed_ip = resource.Body('fixed_ip')
    #: Host
    host = resource.Body('host')
    #: The local ip address
    local_ip_address = resource.Body('local_ip_address')
    #: The ID of Local IP address
    local_ip_id = resource.URI('local_ip_id')
