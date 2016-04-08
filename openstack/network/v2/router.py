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
from openstack import utils


class Router(resource.Resource):
    resource_key = 'router'
    resources_key = 'routers'
    base_path = '/routers'
    service = network_service.NetworkService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True

    # Properties
    #: Availability zone hints to use when scheduling the router.
    #: *Type: list of availability zone names*
    availability_zone_hints = resource.prop('availability_zone_hints')
    #: Availability zones for the router.
    #: *Type: list of availability zone names*
    availability_zones = resource.prop('availability_zones')
    #: The router description.
    description = resource.prop('description')
    #: The ``network_id``, for the external gateway. *Type: dict*
    external_gateway_info = resource.prop('external_gateway_info', type=dict)
    #: The administrative state of the router, which is up ``True``
    #: or down ``False``. *Type: bool*
    is_admin_state_up = resource.prop('admin_state_up', type=bool)
    #: The distributed state of the router, which is distributed ``True``
    #: or not ``False``. *Type: bool* *Default: False*
    is_distributed = resource.prop('distributed', type=bool, default=False)
    #: The highly-available state of the router, which is highly available
    #: ``True`` or not ``False``. *Type: bool* *Default: False*
    is_ha = resource.prop('ha', type=bool, default=False)
    #: The router name.
    name = resource.prop('name')
    #: The ID of the project this router is associated with.
    project_id = resource.prop('tenant_id')
    #: The extra routes configuration for the router.
    routes = resource.prop('routes', type=list)
    #: The router status.
    status = resource.prop('status')

    def add_interface(self, session, **body):
        """Add an internal interface to a logical router.

        :param session: The session to communicate through.
        :type session: :class:`~openstack.session.Session`
        :param dict body : The body requested to be updated on the outer

        :returns: The body of the response as a dictionary.
        """
        url = utils.urljoin(self.base_path, self.id, 'add_router_interface')
        resp = session.put(url, endpoint_filter=self.service, json=body)
        return resp.json()

    def remove_interface(self, session, **body):
        """Remove an internal interface from a logical router.

        :param session: The session to communicate through.
        :type session: :class:`~openstack.session.Session`
        :param dict body : The body requested to be updated on the outer

        :returns: The body of the response as a dictionary.
        """
        url = utils.urljoin(self.base_path, self.id, 'remove_router_interface')
        resp = session.put(url, endpoint_filter=self.service, json=body)
        return resp.json()
