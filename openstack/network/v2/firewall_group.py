# Copyright (c) 2018 China Telecom Corporation
# All Rights Reserved.
#
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


class FirewallGroup(resource.Resource):
    resource_key = 'firewall_group'
    resources_key = 'firewall_groups'
    base_path = '/fwaas/firewall_groups'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'description', 'egress_firewall_policy_id',
        'ingress_firewall_policy_id', 'name', 'shared', 'status', 'ports',
        'project_id')

    # Properties
    #: The administrative state of the firewall group, which is up (true) or
    #: down (false). Default is true.
    admin_state_up = resource.Body('admin_state_up')
    #: The firewall group rule description.
    description = resource.Body('description')
    #: The ID of the egress firewall policy for the firewall group.
    egress_firewall_policy_id = resource.Body('egress_firewall_policy_id')
    #: The ID of the ingress firewall policy for the firewall group.
    ingress_firewall_policy_id = resource.Body('ingress_firewall_policy_id')
    #: The ID of the firewall group.
    id = resource.Body('id')
    #: The name of a firewall group
    name = resource.Body('name')
    #: A list of the IDs of the ports associated with the firewall group.
    ports = resource.Body('ports')
    #: The ID of the project that owns the resource.
    project_id = resource.Body('project_id')
    #: Indicates whether this firewall group is shared across all projects.
    shared = resource.Body('shared')
    #: The status of the firewall group. Valid values are ACTIVE, INACTIVE,
    #: ERROR, PENDING_UPDATE, or PENDING_DELETE.
    status = resource.Body('status')
