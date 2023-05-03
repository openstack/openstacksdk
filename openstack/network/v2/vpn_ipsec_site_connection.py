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


class VpnIPSecSiteConnection(resource.Resource):
    resource_key = 'ipsec_site_connection'
    resources_key = 'ipsec_site_connections'
    base_path = '/vpn/ipsec-site-connections'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'auth_mode',
        'description',
        'ikepolicy_id',
        'ipsecpolicy_id',
        'initiator',
        'local_ep_group_id',
        'peer_address',
        'local_id',
        'mtu',
        'name',
        'peer_id',
        'project_id',
        'psk',
        'peer_ep_group_id',
        'route_mode',
        'vpnservice_id',
        'status',
        is_admin_state_up='admin_state_up',
    )

    # Properties
    #: The dead peer detection (DPD) action.
    # A valid value is clear, hold, restart,
    # disabled, or restart-by-peer. Default value is hold.
    action = resource.Body('action')
    #: The authentication mode. A valid value
    # is psk, which is the default.
    auth_mode = resource.Body('auth_mode')
    #: A human-readable description for the resource.
    # Default is an empty string.
    description = resource.Body('description')
    #: A dictionary with dead peer detection (DPD) protocol controls.
    dpd = resource.Body('dpd', type=dict)
    #: The administrative state of the resource,
    # which is up (true) or down (false).
    is_admin_state_up = resource.Body('admin_state_up', type=bool)
    #: The ID of the IKE policy.
    ikepolicy_id = resource.Body('ikepolicy_id')
    #: Indicates whether this VPN can only respond
    # to connections or both respond
    # to and initiate connections. A valid value is
    # response- only or bi-directional. Default is bi-directional.
    initiator = resource.Body('initiator')
    #: The ID of the IPsec policy.
    ipsecpolicy_id = resource.Body('ipsecpolicy_id')
    #: The dead peer detection (DPD) interval, in seconds.
    # A valid value is a positive integer. Default is 30.
    interval = resource.Body('interval', type=int)
    #: The ID for the endpoint group that contains
    # private subnets for the local side of the connection.
    # Yo must specify this parameter with the
    # peer_ep_group_id parameter unless in backward- compatible
    # mode where peer_cidrs is provided with
    # a subnet_id for the VPN service.
    local_ep_group_id = resource.Body('local_ep_group_id')
    #: The peer gateway public IPv4 or IPv6 address or FQDN.
    peer_address = resource.Body('peer_address')
    #: An ID to be used instead of the external IP address for
    # a virtual router used in traffic between
    # instances on different networks in east-west traffic.
    # Most often, local ID would be domain
    # name, email address, etc. If this is not configured
    # then the external IP address will be used as the ID.
    local_id = resource.Body('local_id')
    #: The maximum transmission unit (MTU)
    # value to address fragmentation. Minimum value
    # is 68 for IPv4, and 1280 for IPv6.
    mtu = resource.Body('mtu', type=int)
    #: Human-readable name of the resource. Default is an empty string.
    name = resource.Body('name')
    #: The peer router identity for authentication.
    # A valid value is an IPv4 address, IPv6 address, e-mail address,
    # key ID, or FQDN. Typically, this value matches
    # the peer_address value.
    peer_id = resource.Body('peer_id')
    #: (Deprecated) Unique list of valid peer private
    # CIDRs in the form < net_address > / < prefix > .
    peer_cidrs = resource.Body('peer_cidrs', type=list)
    #: The ID of the project.
    project_id = resource.Body('tenant_id')
    #: The pre-shared key. A valid value is any string.
    psk = resource.Body('psk')
    #: The ID for the endpoint group that contains
    # private CIDRs in the form < net_address > / < prefix >
    # for the peer side of the connection. You must
    # specify this parameter with the local_ep_group_id
    # parameter unless in backward-compatible mode
    # where peer_cidrs is provided with a subnet_id for the VPN service.
    peer_ep_group_id = resource.Body('peer_ep_group_id')
    #: The route mode. A valid value is static, which is the default.
    route_mode = resource.Body('route_mode')
    #: The site connection status
    status = resource.Body('status')
    #: The dead peer detection (DPD) timeout
    # in seconds. A valid value is a
    # positive integer that is greater
    # than the DPD interval value. Default is 120.
    timeout = resource.Body('timeout', type=int)
    #: The ID of the VPN service.
    vpnservice_id = resource.Body('vpnservice_id')
