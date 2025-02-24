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


class ZoneNameserver(_base.Resource):
    """DNS Zone Nameserver resource"""

    resources_key = 'nameservers'
    base_path = '/zones/%(zone_id)s/nameservers'

    # capabilities
    allow_list = True

    _query_mapping = resource.QueryParameters(
        include_pagination_defaults=False,
    )

    #: ID for the zone
    zone_id = resource.URI('zone_id')
    #: The hostname of the nameserver
    #: *Type: str*
    hostname = resource.Body('hostname')
    #: The priority of the nameserver
    #: *Type: int*
    priority = resource.Body('priority')
