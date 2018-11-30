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


class FloatingIP(resource.Resource, resource.TagMixin):
    name_attribute = "floating_ip_address"
    resource_name = "floating ip"
    resource_key = 'floatingip'
    resources_key = 'floatingips'
    base_path = '/floatingips'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'description', 'fixed_ip_address',
        'floating_ip_address', 'floating_network_id',
        'port_id', 'router_id', 'status', 'subnet_id',
        project_id='tenant_id',
        **resource.TagMixin._tag_query_parameters)

    # Properties
    #: Timestamp at which the floating IP was created.
    created_at = resource.Body('created_at')
    #: The floating IP description.
    description = resource.Body('description')
    #: The DNS domain.
    dns_domain = resource.Body('dns_domain')
    #: The DNS name.
    dns_name = resource.Body('dns_name')
    #: The fixed IP address associated with the floating IP. If you
    #: intend to associate the floating IP with a fixed IP at creation
    #: time, then you must indicate the identifier of the internal port.
    #: If an internal port has multiple associated IP addresses, the
    #: service chooses the first IP unless you explicitly specify the
    #: parameter fixed_ip_address to select a specific IP.
    fixed_ip_address = resource.Body('fixed_ip_address')
    #: The floating IP address.
    floating_ip_address = resource.Body('floating_ip_address')
    #: Floating IP object doesn't have name attribute, set ip address to name
    #: so that user could find floating IP by UUID or IP address using find_ip
    name = floating_ip_address
    #: The ID of the network associated with the floating IP.
    floating_network_id = resource.Body('floating_network_id')
    #: Read-only. The details of the port that this floating IP associates
    #: with. Present if ``fip-port-details`` extension is loaded.
    #: *Type: dict with keys: name, network_id, mac_address, admin_state_up,
    #: status, device_id, device_owner*
    port_details = resource.Body('port_details', type=dict)
    #: The port ID.
    port_id = resource.Body('port_id')
    #: The ID of the QoS policy attached to the floating IP.
    qos_policy_id = resource.Body('qos_policy_id')
    #: The ID of the project this floating IP is associated with.
    project_id = resource.Body('tenant_id')
    #: Revision number of the floating IP. *Type: int*
    revision_number = resource.Body('revision_number', type=int)
    #: The ID of an associated router.
    router_id = resource.Body('router_id')
    #: The floating IP status. Value is ``ACTIVE`` or ``DOWN``.
    status = resource.Body('status')
    #: Timestamp at which the floating IP was last updated.
    updated_at = resource.Body('updated_at')
    #: The Subnet ID associated with the floating IP.
    subnet_id = resource.Body('subnet_id')

    @classmethod
    def find_available(cls, session):
        # server-side filtering on empty values is not always supported.
        # TODO(mordred) Make this check for support for the server-side filter
        for ip in cls.list(session):
            if not ip.port_id:
                return ip
        return None
