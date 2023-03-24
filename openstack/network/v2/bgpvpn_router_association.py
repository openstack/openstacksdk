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


class BgpVpnRouterAssociation(resource.Resource):
    resource_key = 'router_association'
    resources_key = 'router_associations'
    base_path = '/bgpvpn/bgpvpns/%(bgpvpn_id)s/router_associations'

    _allow_unknown_attrs_in_body = True

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    # Properties
    #: The Id of the BGPVPN
    id = resource.Body('id')
    #: The ID of the BGPVPN who owns Network Association.
    bgpvpn_id = resource.URI('bgpvpn_id')
    #: The ID of the project that owns the BGPVPN
    project_id = resource.Body('project_id', alias='tenant_id')
    #: Tenant_id (deprecated attribute).
    tenant_id = resource.Body('tenant_id', deprecated=True)
    #: The ID of a Neutron router with which to associate the BGP VPN.
    router_id = resource.Body('router_id')
    #: Boolean flag controlling whether or not the routes specified in the
    #: routes attribute of the router will be advertised to the BGPVPN
    #: (default: true).
    advertise_extra_routes = resource.Body('advertise_extra_routes')
