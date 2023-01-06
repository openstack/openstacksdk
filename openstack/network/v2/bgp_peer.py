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


class BgpPeer(resource.Resource):
    resource_key = 'bgp_peer'
    resources_key = 'bgp_peers'
    base_path = '/bgp-peers'

    _allow_unknown_attrs_in_body = True

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    # Properties
    #: The Id of the BGP Peer
    id = resource.Body('id')
    #: The BGP Peer's name.
    name = resource.Body('name')
    #: The ID of the project that owns the BGP Peer
    project_id = resource.Body('project_id', alias='tenant_id')
    #: Tenant_id (deprecated attribute).
    tenant_id = resource.Body('tenant_id', deprecated=True)
    #: The authentication type for the BGP Peer, can be none or md5.
    #: none by default.
    auth_type = resource.Body('auth_type')
    #: The remote Autonomous System number of the BGP Peer.
    remote_as = resource.Body('remote_as')
    #: The ip address of the Peer.
    peer_ip = resource.Body('peer_ip')
