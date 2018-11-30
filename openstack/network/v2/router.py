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
from openstack import utils


class Router(resource.Resource, resource.TagMixin):
    resource_key = 'router'
    resources_key = 'routers'
    base_path = '/routers'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    # NOTE: We don't support query on datetime, list or dict fields
    _query_mapping = resource.QueryParameters(
        'description', 'flavor_id', 'name', 'status',
        is_admin_state_up='admin_state_up',
        is_distributed='distributed',
        is_ha='ha',
        project_id='tenant_id',
        **resource.TagMixin._tag_query_parameters
    )

    # Properties
    #: Availability zone hints to use when scheduling the router.
    #: *Type: list of availability zone names*
    availability_zone_hints = resource.Body('availability_zone_hints',
                                            type=list)
    #: Availability zones for the router.
    #: *Type: list of availability zone names*
    availability_zones = resource.Body('availability_zones', type=list)
    #: Timestamp when the router was created.
    created_at = resource.Body('created_at')
    #: The router description.
    description = resource.Body('description')
    #: The ``network_id``, for the external gateway. *Type: dict*
    external_gateway_info = resource.Body('external_gateway_info', type=dict)
    #: The ID of the flavor.
    flavor_id = resource.Body('flavor_id')
    #: The administrative state of the router, which is up ``True``
    #: or down ``False``. *Type: bool*
    is_admin_state_up = resource.Body('admin_state_up', type=bool)
    #: The distributed state of the router, which is distributed ``True``
    #: or not ``False``. *Type: bool*
    is_distributed = resource.Body('distributed', type=bool)
    #: The highly-available state of the router, which is highly available
    #: ``True`` or not ``False``. *Type: bool*
    is_ha = resource.Body('ha', type=bool)
    #: The router name.
    name = resource.Body('name')
    #: The ID of the project this router is associated with.
    project_id = resource.Body('tenant_id')
    #: Revision number of the router. *Type: int*
    revision_number = resource.Body('revision', type=int)
    #: The extra routes configuration for the router.
    routes = resource.Body('routes', type=list)
    #: The router status.
    status = resource.Body('status')
    #: Timestamp when the router was created.
    updated_at = resource.Body('updated_at')

    def add_interface(self, session, **body):
        """Add an internal interface to a logical router.

        :param session: The session to communicate through.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param dict body: The body requested to be updated on the router

        :returns: The body of the response as a dictionary.
        """
        url = utils.urljoin(self.base_path, self.id, 'add_router_interface')
        resp = session.put(url, json=body)
        return resp.json()

    def remove_interface(self, session, **body):
        """Remove an internal interface from a logical router.

        :param session: The session to communicate through.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param dict body: The body requested to be updated on the router

        :returns: The body of the response as a dictionary.
        """
        url = utils.urljoin(self.base_path, self.id, 'remove_router_interface')
        resp = session.put(url, json=body)
        return resp.json()

    def add_gateway(self, session, **body):
        """Add an external gateway to a logical router.

        :param session: The session to communicate through.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param dict body: The body requested to be updated on the router

        :returns: The body of the response as a dictionary.
        """
        url = utils.urljoin(self.base_path, self.id,
                            'add_gateway_router')
        resp = session.put(url, json=body)
        return resp.json()

    def remove_gateway(self, session, **body):
        """Remove an external gateway from a logical router.

        :param session: The session to communicate through.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param dict body: The body requested to be updated on the router

        :returns: The body of the response as a dictionary.
        """
        url = utils.urljoin(self.base_path, self.id,
                            'remove_gateway_router')
        resp = session.put(url, json=body)
        return resp.json()


class L3AgentRouter(Router):
    resource_key = 'router'
    resources_key = 'routers'
    base_path = '/agents/%(agent_id)s/l3-routers'
    resource_name = 'l3-router'

    # capabilities
    allow_create = False
    allow_retrieve = True
    allow_commit = False
    allow_delete = False
    allow_list = True

# NOTE: No query parameter is supported
