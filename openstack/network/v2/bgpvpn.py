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


class BgpVpn(resource.Resource):
    resource_key = 'bgpvpn'
    resources_key = 'bgpvpns'
    base_path = '/bgpvpn/bgpvpns'

    _allow_unknown_attrs_in_body = True

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'name',
        'project_id',
        'local_pref',
        'vni',
        'type',
        'networks',
        'routers',
        'ports',
        # NOTE(seba): (route|import|export) targets only support exact matches
        # and have therefore been left out
    )

    # Properties
    #: The Id of the BGPVPN
    id = resource.Body('id')
    #: The BGPVPN's name.
    name = resource.Body('name')
    #: The ID of the project that owns the BGPVPN
    project_id = resource.Body('project_id', alias='tenant_id')
    #: Tenant_id (deprecated attribute).
    tenant_id = resource.Body('tenant_id', deprecated=True)
    #: List of route distinguisher strings.
    route_distinguishers = resource.Body('route_distinguishers')
    #: Route Targets that will be both imported and used for export.
    route_targets = resource.Body('route_targets')
    #: Additional Route Targets that will be imported.
    import_targets = resource.Body('import_targets')
    #: Additional Route Targets that will be used for export.
    export_targets = resource.Body('export_targets')
    #: The default BGP LOCAL_PREF of routes that will be advertised to
    #: the BGPVPN.
    local_pref = resource.Body('local_pref')
    #: The globally-assigned VXLAN vni for the BGP VPN.
    vni = resource.Body('vni')
    #: Selection of the type of VPN and the technology behind it.
    #: Allowed values are l2 or l3.
    type = resource.Body('type')
