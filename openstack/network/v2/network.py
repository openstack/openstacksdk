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

from openstack.network import network_service
from openstack import resource


class Network(resource.Resource):
    resource_key = 'network'
    resources_key = 'networks'
    base_path = '/networks'
    service = network_service.NetworkService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True

    # Properties
    #: The administrative state of the network, which is up ``True`` or
    #: down ``False``. *Type: bool*
    admin_state_up = resource.prop('admin_state_up', type=bool)
    #: Availability zone hints to use when scheduling the network.
    #: *Type: list of availability zone names*
    availability_zone_hints = resource.prop('availability_zone_hints')
    #: Availability zones for the network.
    #: *Type: list of availability zone names*
    availability_zones = resource.prop('availability_zones')
    #: The network name.
    name = resource.prop('name')
    #: The ID of the project this network is associated with.
    project_id = resource.prop('tenant_id')
    #: The type of physical network that maps to this network resource.
    #: For example, ``flat``, ``vlan``, ``vxlan``, or ``gre``.
    provider_network_type = resource.prop('provider:network_type')
    #: The physical network where this network object is implemented.
    provider_physical_network = resource.prop('provider:physical_network')
    #: An isolated segment ID on the physical network. The provider
    #: network type defines the segmentation model.
    provider_segmentation_id = resource.prop('provider:segmentation_id')
    #: Whether or not the router is external. *Type: bool*
    router_external = resource.prop('router:external')
    #: Whether or not the router is 'External' or 'Internal'.
    router_type = resource.prop('router_type')
    segments = resource.prop('segments')
    #: Indicates whether this network is shared across all tenants.
    #: By default, only administrative users can change this value.
    #: *Type: bool*
    shared = resource.prop('shared', type=bool)
    #: The network status.
    status = resource.prop('status')
    #: The associated subnet IDs.
    #: *Type: list of strs of the subnet IDs*
    subnet_ids = resource.prop('subnets', type=list)
    #: Read-only. The maximum transmission unit (MTU) of the network resource.
    mtu = resource.prop('mtu', type=int)
    #: The port security status, which is enabled ``True`` or disabled
    #: ``False``. *Type: bool* *Default: False*
    is_port_security_enabled = resource.prop('port_security_enabled',
                                             type=bool,
                                             default=False)

    def is_external(self):
        if self.router_external is not None:
            return bool(self.router_external)
        if self.router_type == 'External':
            return True
        return False
