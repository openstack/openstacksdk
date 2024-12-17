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


class Limit(_base.Resource):
    """DNS Limit Resource"""

    resource_key = 'limit'
    base_path = '/limits'

    # capabilities
    allow_list = True

    #: Properties
    #: The max amount of items allowed per page
    max_page_limit = resource.Body('max_page_limit', type=int)
    #: The max length of a recordset name
    max_recordset_name_length = resource.Body(
        'max_recordset_name_length', type=int
    )
    #: The max amount of records contained in a recordset
    max_recordset_records = resource.Body('max_recordset_records', type=int)
    #: The max length of a zone name
    max_zone_name_length = resource.Body('max_zone_name_length', type=int)
    #: The max amount of records in a zone
    max_zone_records = resource.Body('max_zone_records', type=int)
    #: The max amount of recordsets per zone
    max_zone_recordsets = resource.Body('max_zone_recordsets', type=int)
    #: The max amount of zones for this project
    max_zones = resource.Body('max_zones', type=int)
    #: The lowest ttl allowed on this system
    min_ttl = resource.Body('min_ttl', type=int)
