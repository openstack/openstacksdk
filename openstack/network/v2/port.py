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
from openstack.network.v2 import tag
from openstack import resource


class Port(resource.Resource, tag.TagMixin):
    resource_key = 'port'
    resources_key = 'ports'
    base_path = '/ports'
    service = network_service.NetworkService()

    # capabilities
    allow_create = True
    allow_get = True
    allow_update = True
    allow_delete = True
    allow_list = True

    # NOTE: we skip query on list or datetime fields for now
    _query_mapping = resource.QueryParameters(
        'binding:host_id', 'binding:profile', 'binding:vif_details',
        'binding:vif_type', 'binding:vnic_type',
        'description', 'device_id', 'device_owner', 'fixed_ips', 'ip_address',
        'mac_address', 'name', 'network_id', 'status', 'subnet_id',
        is_admin_state_up='admin_state_up',
        is_port_security_enabled='port_security_enabled',
        project_id='tenant_id',
        **tag.TagMixin._tag_query_parameters
    )

    # Properties
    #: Allowed address pairs.
    allowed_address_pairs = resource.Body('allowed_address_pairs', type=list)
    #: The ID of the host where the port is allocated. In some cases,
    #: different implementations can run on different hosts.
    binding_host_id = resource.Body('binding:host_id')
    #: A dictionary the enables the application running on the specified
    #: host to pass and receive vif port-specific information to the plug-in.
    #: *Type: dict*
    binding_profile = resource.Body('binding:profile', type=dict)
    #: Read-only. A dictionary that enables the application to pass
    #: information about functions that the Networking API provides.
    #: To enable or disable port filtering features such as security group
    #: and anti-MAC/IP spoofing, specify ``port_filter: True`` or
    #: ``port_filter: False``. *Type: dict*
    binding_vif_details = resource.Body('binding:vif_details', type=dict)
    #: Read-only. The vif type for the specified port.
    binding_vif_type = resource.Body('binding:vif_type')
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
    binding_vnic_type = resource.Body('binding:vnic_type')
    #: Timestamp when the port was created.
    created_at = resource.Body('created_at')
    #: Underlying data plane status of this port.
    data_plane_status = resource.Body('data_plane_status')
    #: The port description.
    description = resource.Body('description')
    #: Device ID of this port.
    device_id = resource.Body('device_id')
    #: Device owner of this port (e.g. ``network:dhcp``).
    device_owner = resource.Body('device_owner')
    #: DNS assignment for the port.
    dns_assignment = resource.Body('dns_assignment')
    #: DNS domain assigned to the port.
    dns_domain = resource.Body('dns_domain')
    #: DNS name for the port.
    dns_name = resource.Body('dns_name')
    #: Extra DHCP options.
    extra_dhcp_opts = resource.Body('extra_dhcp_opts', type=list)
    #: IP addresses for the port. Includes the IP address and subnet ID.
    fixed_ips = resource.Body('fixed_ips', type=list)
    #: The administrative state of the port, which is up ``True`` or
    #: down ``False``. *Type: bool*
    is_admin_state_up = resource.Body('admin_state_up', type=bool)
    #: The port security status, which is enabled ``True`` or disabled
    #: ``False``. *Type: bool* *Default: False*
    is_port_security_enabled = resource.Body('port_security_enabled',
                                             type=bool, default=False)
    #: The MAC address of an allowed address pair.
    mac_address = resource.Body('mac_address')
    #: The port name.
    name = resource.Body('name')
    #: The ID of the attached network.
    network_id = resource.Body('network_id')
    #: The ID of the project who owns the network. Only administrative
    #: users can specify a project ID other than their own.
    project_id = resource.Body('tenant_id')
    #: The ID of the QoS policy attached to the port.
    qos_policy_id = resource.Body('qos_policy_id')
    #: Revision number of the port. *Type: int*
    revision_number = resource.Body('revision_number', type=int)
    #: The IDs of any attached security groups.
    #: *Type: list of strs of the security group IDs*
    security_group_ids = resource.Body('security_groups', type=list)
    #: The port status. Value is ``ACTIVE`` or ``DOWN``.
    status = resource.Body('status')
    #: Read-only. The trunk referring to this parent port and its subports.
    #: Present for trunk parent ports if ``trunk-details`` extension is loaded.
    #: *Type: dict with keys: trunk_id, sub_ports.
    #: sub_ports is a list of dicts with keys:
    #: port_id, segmentation_type, segmentation_id, mac_address*
    trunk_details = resource.Body('trunk_details', type=dict)
    #: Timestamp when the port was last updated.
    updated_at = resource.Body('updated_at')
