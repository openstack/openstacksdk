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


class Port(resource.Resource):
    resource_key = 'port'
    resources_key = 'ports'
    base_path = '/ports'
    service = network_service.NetworkService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True

    # Properties
    #: The administrative state of the port, which is up ``True`` or
    #: down ``False``. *Type: bool*
    admin_state_up = resource.prop('admin_state_up', type=bool)
    #: Allowed address pairs. *Type: dict*
    allowed_address_pairs = resource.prop('allowed_address_pairs', type=dict)
    #: The ID of the host where the port is allocated. In some cases,
    #: different implementations can run on different hosts.
    binding_host_id = resource.prop('binding:host_id')
    #: A dictionary the enables the application running on the specified
    #: host to pass and receive vif port-specific information to the plug-in.
    binding_profile = resource.prop('binding:profile')
    #: Read-only. A dictionary that enables the application to pass
    #: information about functions that the Networking API provides.
    #: To enable or disable port filtering features such as security group
    #: and anti-MAC/IP spoofing, specify ``port_filter: True`` or
    #: ``port_filter: False``.
    binding_vif_details = resource.prop('binding:vif_details', type=dict)
    #: Read-only. The vif type for the specified port.
    binding_vif_type = resource.prop('binding:vif_type')
    #: The vnic type that is bound to the neutron port.
    #:
    #: In POST and PUT operations, specify a value of ``normal`` (virtual nic),
    #: ``direct`` (pci passthrough), or ``macvtap``
    #: (virtual interface with a tap-like software interface).
    #: These values support SR-IOV PCI passthrough networking.
    #: The ML2 plug-in supports the vnic_type.
    #:
    #: In GET operations, the binding:vnic_type extended attribute is
    #: visible to only port owners and administrative users.
    binding_vnic_type = resource.prop('binding:vnic_type')
    #: The ID of the device that uses this port. For example, a virtual server.
    device_id = resource.prop('device_id')
    #: The ID of the entity that uses this port. For example, a dhcp agent.
    device_owner = resource.prop('device_owner')
    #: Extra DHCP options.
    extra_dhcp_opts = resource.prop('extra_dhcp_opts', type=dict)
    #: IP addresses for the port. Includes the IP address and subnet ID.
    fixed_ips = resource.prop('fixed_ips')
    #: The MAC address of the port.
    mac_address = resource.prop('mac_address')
    #: The port name.
    name = resource.prop('name')
    #: The ID of the attached network.
    network_id = resource.prop('network_id')
    #: The ID of the project who owns the network. Only administrative
    #: users can specify a project ID other than their own.
    project_id = resource.prop('tenant_id')
    #: The IDs of any attached security groups.
    security_groups = resource.prop('security_groups')
    #: The port status. Value is ``ACTIVE`` or ``DOWN``.
    status = resource.prop('status')
