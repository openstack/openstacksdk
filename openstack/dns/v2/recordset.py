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

from openstack.dns import dns_service
from openstack import resource2 as resource


class Recordset(resource.Resource):
    """Recordset Resource"""
    resource_key = 'recordset'
    resources_key = 'recordsets'
    base_path = '/zones/%(zone_id)s/recordsets'
    service = dns_service.DNSService()

    # capabilities
    allow_create = True
    allow_list = True
    allow_get = True
    allow_delete = True

    #: Properties
    #: The id of the Zone which this recordset belongs to
    zone_id = resource.URI('zone_id')
    #: Recordset name
    name = resource.Body('name')
    #: Recordset description
    description = resource.Body('description')
    #: DNS type of the recordset
    #: Valid values include ``A``, ``AAA``, ``MX``, ``CNAME``, ``TXT``, ``NS``
    type = resource.Body('type')
    #: Time to live, default 300, available value 300-2147483647 (seconds)
    ttl = resource.Body('ttl', type=int)
    #: DNS record value list
    records = resource.Body('records', type=list)
    #: Recordset status
    #: Valid values include ``PENDING_CREATE``, ``ACTIVE``,
    #:                       ``PENDING_DELETE``, ``ERROR``
    status = resource.Body('status')
    #: The name of the Zone which this recordset belongs to
    zone_name = resource.Body('zone_name')
    #: Is the recordset created by system.
    is_default = resource.Body('default', type=bool)
    #: Health check id, not support for now
    health_check_id = resource.Body('health_check_id')
    #: Links contains a `self` pertaining to this zone or a `next` pertaining
    #: to next page
    links = resource.Body('links', type=dict)
    #: ID of the project which the recordset belongs to
    project_id = resource.Body('project_id')
    #: Timestamp when the zone was created
    created_at = resource.Body('created_at')
    #: Timestamp when the zone was last updated
    updated_at = resource.Body('updated_at')


class Recordsets(Recordset):
    """Recordsets resource represent list all recordset API response"""
    base_path = '/recordsets'
