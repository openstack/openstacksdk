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

from openstack import exceptions
from openstack.network.v2 import _base
from openstack import resource
from openstack import utils


class Router(_base.NetworkResource, _base.TagMixinNetwork):
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
        'description',
        'flavor_id',
        'name',
        'status',
        'project_id',
        'sort_key',
        'sort_dir',
        is_admin_state_up='admin_state_up',
        is_distributed='distributed',
        is_ha='ha',
        **_base.TagMixinNetwork._tag_query_parameters,
    )

    # Properties
    #: Availability zone hints to use when scheduling the router.
    #: *Type: list of availability zone names*
    availability_zone_hints = resource.Body(
        'availability_zone_hints', type=list
    )
    #: Availability zones for the router.
    #: *Type: list of availability zone names*
    availability_zones = resource.Body('availability_zones', type=list)
    #: Timestamp when the router was created.
    created_at = resource.Body('created_at')
    #: The router description.
    description = resource.Body('description')
    #: The ndp proxy state of the router
    enable_ndp_proxy = resource.Body('enable_ndp_proxy', type=bool)
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
    project_id = resource.Body('project_id', alias='tenant_id')
    #: Tenant_id (deprecated attribute).
    tenant_id = resource.Body('tenant_id', deprecated=True)
    #: Revision number of the router. *Type: int*
    revision_number = resource.Body('revision', type=int)
    #: The extra routes configuration for the router.
    routes = resource.Body('routes', type=list)
    #: The router status.
    status = resource.Body('status')
    #: Timestamp when the router was created.
    updated_at = resource.Body('updated_at')

    def _put(self, session, url, body):
        resp = session.put(url, json=body)
        exceptions.raise_from_response(resp)
        return resp

    def add_interface(self, session, **body):
        """Add an internal interface to a logical router.

        :param session: The session to communicate through.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param dict body: The body requested to be updated on the router

        :returns: The body of the response as a dictionary.

        :raises: :class:`~openstack.exceptions.SDKException` on error.
        """
        url = utils.urljoin(self.base_path, self.id, 'add_router_interface')
        resp = self._put(session, url, body)
        return resp.json()

    def remove_interface(self, session, **body):
        """Remove an internal interface from a logical router.

        :param session: The session to communicate through.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param dict body: The body requested to be updated on the router

        :returns: The body of the response as a dictionary.

        :raises: :class:`~openstack.exceptions.SDKException` on error.
        """
        url = utils.urljoin(self.base_path, self.id, 'remove_router_interface')
        resp = self._put(session, url, body)
        return resp.json()

    def add_extra_routes(self, session, body):
        """Add extra routes to a logical router.

        :param session: The session to communicate through.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param dict body: The request body as documented in the api-ref.

        :returns: The response as a Router object with the added extra routes.

        :raises: :class:`~openstack.exceptions.SDKException` on error.
        """
        url = utils.urljoin(self.base_path, self.id, 'add_extraroutes')
        resp = self._put(session, url, body)
        self._translate_response(resp)
        return self

    def remove_extra_routes(self, session, body):
        """Remove extra routes from a logical router.

        :param session: The session to communicate through.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param dict body: The request body as documented in the api-ref.

        :returns: The response as a Router object with the extra routes left.

        :raises: :class:`~openstack.exceptions.SDKException` on error.
        """
        url = utils.urljoin(self.base_path, self.id, 'remove_extraroutes')
        resp = self._put(session, url, body)
        self._translate_response(resp)
        return self

    def add_gateway(self, session, **body):
        """Add an external gateway to a logical router.

        :param session: The session to communicate through.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param dict body: The body requested to be updated on the router

        :returns: The body of the response as a dictionary.
        """
        url = utils.urljoin(self.base_path, self.id, 'add_gateway_router')
        resp = session.put(url, json=body)
        return resp.json()

    def remove_gateway(self, session, **body):
        """Remove an external gateway from a logical router.

        :param session: The session to communicate through.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param dict body: The body requested to be updated on the router

        :returns: The body of the response as a dictionary.
        """
        url = utils.urljoin(self.base_path, self.id, 'remove_gateway_router')
        resp = session.put(url, json=body)
        return resp.json()

    def add_external_gateways(self, session, body):
        """Add external gateways to a router.

        :param session: The session to communicate through.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param dict body: The body requested to be updated on the router

        :returns: The body of the response as a dictionary.
        """
        url = utils.urljoin(self.base_path, self.id, 'add_external_gateways')
        resp = session.put(url, json=body)
        self._translate_response(resp)
        return self

    def update_external_gateways(self, session, body):
        """Update external gateways of a router.

        :param session: The session to communicate through.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param dict body: The body requested to be updated on the router

        :returns: The body of the response as a dictionary.
        """
        url = utils.urljoin(
            self.base_path, self.id, 'update_external_gateways'
        )
        resp = session.put(url, json=body)
        self._translate_response(resp)
        return self

    def remove_external_gateways(self, session, body):
        """Remove external gateways from a router.

        :param session: The session to communicate through.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param dict body: The body requested to be updated on the router

        :returns: The body of the response as a dictionary.
        """
        url = utils.urljoin(
            self.base_path, self.id, 'remove_external_gateways'
        )
        resp = session.put(url, json=body)
        self._translate_response(resp)
        return self


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
