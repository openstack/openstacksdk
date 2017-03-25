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
from openstack import resource2 as resource


class FloatingIP(resource.Resource):
    name_attribute = "floating_ip_address"
    resource_name = "floating ip"
    resource_key = 'floatingip'
    resources_key = 'floatingips'
    base_path = '/floatingips'
    service = network_service.NetworkService()

    # capabilities
    allow_create = True
    allow_get = True
    allow_update = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'description', 'fixed_ip_address', 'floating_ip_address',
        'floating_network_id', 'port_id', 'router_id', 'status',
        project_id='tenant_id')

    # Properties
    #: Timestamp at which the floating IP was created.
    created_at = resource.Body('created_at')
    #: The floating IP description.
    description = resource.Body('description')
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
    #: The port ID.
    port_id = resource.Body('port_id')
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

    @classmethod
    def find_available(cls, session):
        info = cls.list(session, fields='id', port_id='')
        try:
            return next(info)
        except StopIteration:
            return None
