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


class ShareNetworkSubnet(resource.Resource):
    resource_key = "share_network_subnet"
    resources_key = "share_network_subnets"
    base_path = "/share-networks/%(share_network_id)s/subnets"

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = False
    allow_delete = True
    allow_list = True

    #: Properties
    #: The share nerwork ID, part of the URI for share network subnets.
    share_network_id = resource.URI("share_network_id", type=str)

    #: The name of the availability zone that the share network
    #: subnet belongs to.
    availability_zone = resource.Body("availability_zone", type=str)
    #: The IP block from which to allocate the network, in CIDR notation.
    cidr = resource.Body("cidr", type=str)
    #: Date and time the share network subnet was created at.
    created_at = resource.Body("created_at")
    #: The gateway of a share network subnet.
    gateway = resource.Body("gateway", type=str)
    #: The IP version of the network.
    ip_version = resource.Body("ip_version", type=int)
    #: The MTU of a share network subnet.
    mtu = resource.Body("mtu", type=str)
    #: The network type. A valid value is VLAN, VXLAN, GRE, or flat
    network_type = resource.Body("network_type", type=str)
    #: The name of the neutron network.
    neutron_net_id = resource.Body("neutron_net_id", type=str)
    #: The ID of the neitron subnet.
    neutron_subnet_id = resource.Body("neutron_subnet_id", type=str)
    #: The segmentation ID.
    segmentation_id = resource.Body('segmentation_id', type=int)
    #: The name of the share network that the share network subnet belongs to.
    share_network_name = resource.Body("share_network_name", type=str)
    #: Date and time the share network subnet was last updated at.
    updated_at = resource.Body("updated_at", type=str)

    def create(
        self,
        session,
        *args,
        resource_request_key='share-network-subnet',
        **kwargs,
    ):
        return super().create(
            session, resource_request_key=resource_request_key, *args, **kwargs
        )
