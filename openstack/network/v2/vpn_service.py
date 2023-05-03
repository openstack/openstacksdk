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


class VpnService(resource.Resource):
    resource_key = 'vpnservice'
    resources_key = 'vpnservices'
    base_path = '/vpn/vpnservices'

    _allow_unknown_attrs_in_body = True

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'description',
        'external_v4_ip',
        'external_v6_ip',
        'name',
        'router_id',
        'project_id',
        'tenant_id',
        'subnet_id',
        is_admin_state_up='admin_state_up',
    )

    # Properties
    #: Human-readable description for the vpnservice.
    description = resource.Body('description')
    #: The external IPv4 address that is used for the VPN service.
    external_v4_ip = resource.Body('external_v4_ip')
    #: The external IPv6 address that is used for the VPN service.
    external_v6_ip = resource.Body('external_v6_ip')
    #: The administrative state of the vpnservice, which is up ``True`` or
    #: down ``False``. *Type: bool*
    is_admin_state_up = resource.Body('admin_state_up', type=bool)
    #: The vpnservice name.
    name = resource.Body('name')
    #: ID of the router into which the VPN service is inserted.
    router_id = resource.Body('router_id')
    #: The ID of the project this vpnservice is associated with.
    project_id = resource.Body('project_id', alias='tenant_id')
    #: Tenant_id (deprecated attribute).
    tenant_id = resource.Body('tenant_id', deprecated=True)
    #: The vpnservice status.
    status = resource.Body('status')
    #: The ID of the subnet on which the tenant wants the vpnservice.
    subnet_id = resource.Body('subnet_id')
