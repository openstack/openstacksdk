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


class ZoneShare(_base.Resource):
    """DNS ZONE Share Resource"""

    resources_key = 'shared_zones'
    base_path = '/zones/%(zone_id)s/shares'

    # capabilities
    allow_create = True
    allow_delete = True
    allow_fetch = True
    allow_list = True

    _query_mapping = resource.QueryParameters('target_project_id')

    # Properties
    #: The ID of the zone being shared.
    zone_id = resource.URI('zone_id')
    #: Timestamp when the share was created.
    created_at = resource.Body('created_at')
    #: Timestamp when the member was last updated.
    updated_at = resource.Body('updated_at')
    # FIXME(stephenfin): This conflicts since there is a zone ID in the URI
    #: The zone ID of the zone being shared.
    # zone_id = resource.Body('zone_id')
    #: The project ID that owns the share.
    project_id = resource.Body('project_id')
    #: The target project ID that the zone is shared with.
    target_project_id = resource.Body('target_project_id')
