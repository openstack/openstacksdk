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


class FirewallRule(resource.Resource):
    resource_key = 'firewall_rule'
    resources_key = 'firewall_rules'
    base_path = '/fwaas/firewall_rules'

    _allow_unknown_attrs_in_body = True

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'action',
        'description',
        'destination_ip_address',
        'name',
        'destination_port',
        'enabled',
        'ip_version',
        'project_id',
        'protocol',
        'shared',
        'source_ip_address',
        'source_port',
        'firewall_policy_id',
    )

    # Properties
    #: The action that the API performs on traffic that matches the firewall
    #: rule. Valid values are allow or deny. Default is deny.
    action = resource.Body('action')
    #: The description of the firewall rule
    description = resource.Body('description')
    #: The destination IPv4 or IPv6 address or CIDR for the firewall rule.
    destination_ip_address = resource.Body('destination_ip_address')
    #: The destination port or port range for the firewall rule.
    destination_port = resource.Body('destination_port')
    #: Facilitates selectively turning off rules without having to disassociate
    #: the rule from the firewall policy
    enabled = resource.Body('enabled')
    #: The IP protocol version for the firewall rule. Valid values are 4 or 6.
    ip_version = resource.Body('ip_version')
    #: The name of the firewall rule.
    name = resource.Body('name')
    #: The ID of the project that owns the resource.
    project_id = resource.Body('project_id')
    #: The IP protocol for the firewall rule.
    protocol = resource.Body('protocol')
    #: Indicates whether this firewall rule is shared across all projects.
    shared = resource.Body('shared')
    #: The source IPv4 or IPv6 address or CIDR for the firewall rule.
    source_ip_address = resource.Body('source_ip_address')
    #: The source port or port range for the firewall rule.
    source_port = resource.Body('source_port')
    #: Summary field of a FirewallRule, composed of the protocol,
    #: source_ip_address:source_port,
    #: destination_ip_address:destination_port and action.
    summary = resource.Computed('summary', default='')
    #: The ID of the firewall policy.
    firewall_policy_id = resource.Body('firewall_policy_id')
    #: The ID of the firewall rule.
    id = resource.Body('id')
