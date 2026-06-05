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

from keystoneauth1 import adapter

from openstack.dns.v2 import _base
from openstack import resource


class ZoneExport(_base.Resource):
    """DNS Zone Exports Resource"""

    resource_key = ''
    resources_key = 'exports'
    base_path = '/zones/tasks/export'

    create_opts = resource.CreateOpts(request_key=None)

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters('zone_id', 'message', 'status')

    #: Properties
    #: Timestamp when the zone was created
    created_at = resource.Body('created_at')
    #: Links contains a `self` pertaining to this zone or a `next` pertaining
    #: to next page
    links = resource.Body('links', type=dict)
    #: Message
    message = resource.Body('message')
    #: Returns the total_count of resources matching this filter
    metadata = resource.Body('metadata', type=list)
    #: The project id which the zone belongs to
    project_id = resource.Body('project_id')
    #: Current status of the zone export
    status = resource.Body('status')
    #: Timestamp when the zone was last updated
    updated_at = resource.Body('updated_at')
    #: Version of the resource
    version = resource.Body('version', type=int)
    #: ID for the zone that was created by this export
    zone_id = resource.Body('zone_id')

    @classmethod
    def _transform_create_request(
        cls,
        session: adapter.Adapter,
        request: resource._Request,
        *,
        microversion: str | None,
    ) -> resource._Request:
        request.body = None
        return request
