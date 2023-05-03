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


class TapFlow(resource.Resource):
    """Tap Flow"""

    resource_key = 'tap_flow'
    resources_key = 'tap_flows'
    base_path = '/taas/tap_flows'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    _allow_unknown_attrs_in_body = True

    _query_mapping = resource.QueryParameters(
        "sort_key",
        "sort_dir",
        'name',
        'project_id',
    )

    # Properties
    #: The ID of the tap flow.
    id = resource.Body('id')
    #: The tap flow's name.
    name = resource.Body('name')
    #: The tap flow's description.
    description = resource.Body('description')
    #: The ID of the project that owns the tap flow.
    project_id = resource.Body('project_id', alias='tenant_id')
    #: Tenant_id (deprecated attribute).
    tenant_id = resource.Body('tenant_id', deprecated=True)
    #: The id of the tap_service with which the tap flow is associated
    tap_service_id = resource.Body('tap_service_id')
    #: The direction of the tap flow.
    direction = resource.Body('direction')
    #: The status for the tap flow.
    status = resource.Body('status')
    #: The id of the port the tap flow is associated with
    source_port = resource.Body('source_port')
