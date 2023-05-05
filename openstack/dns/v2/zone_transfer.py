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

from openstack.dns.v2 import _base
from openstack import resource


class ZoneTransferBase(_base.Resource):
    """DNS Zone Transfer Request/Accept Base Resource"""

    _query_mapping = resource.QueryParameters('status')

    #: Properties
    #: Timestamp when the resource was created
    created_at = resource.Body('created_at')
    #: Key that is used as part of the zone transfer accept process.
    #: This is only shown to the creator, and must be communicated out of band.
    key = resource.Body('key')
    #: The project id which the zone belongs to
    project_id = resource.Body('project_id')
    #: Current status of the zone import
    status = resource.Body('status')
    #: Timestamp when the resource was last updated
    updated_at = resource.Body('updated_at')
    #: Version of the resource
    version = resource.Body('version', type=int)
    #: ID for the zone that is being exported
    zone_id = resource.Body('zone_id')


class ZoneTransferRequest(ZoneTransferBase):
    """DNS Zone Transfer Request Resource"""

    base_path = '/zones/tasks/transfer_requests'
    resources_key = 'transfer_requests'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_delete = True
    allow_list = True
    allow_commit = True

    #: Description
    description = resource.Body('description')
    #: A project ID that the request will be limited to.
    #: No other project will be allowed to accept this request.
    target_project_id = resource.Body('target_project_id')
    #: Name for the zone that is being exported
    zone_name = resource.Body('zone_name')


class ZoneTransferAccept(ZoneTransferBase):
    """DNS Zone Transfer Accept Resource"""

    base_path = '/zones/tasks/transfer_accepts'
    resources_key = 'transfer_accepts'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_list = True

    #: Name for the zone that is being exported
    zone_transfer_request_id = resource.Body('zone_transfer_request_id')
