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


class Router(resource.Resource):
    """DNS Zone Router Resource"""
    router_id = resource.Body('router_id')
    router_region = resource.Body('router_region')
    status = resource.Body('status')


class Zone(resource.Resource):
    """DNS ZONE Resource"""
    resource_key = 'zone'
    resources_key = 'zones'
    base_path = '/zones'
    service = dns_service.DNSService()

    # capabilities
    allow_create = True
    allow_list = True
    allow_get = True
    allow_delete = True

    _query_mapping = resource.QueryParameters(zone_type='type')

    #: Properties
    #: Zone name
    name = resource.Body('name')
    #: Zone type, if private, domain will only available in a special VPC.
    #: Valid values include ``private``, ``public``
    zone_type = resource.Body('zone_type')
    #: Zone description
    description = resource.Body('description')
    #: The administrator email of this zone
    email = resource.Body('email')
    #: SOA TTL time, unit is seconds, default 300, TTL range 300-2147483647
    ttl = resource.Body('ttl', type=int)
    #: A dictionary represent Router(VPC), includes required items:
    #:  ``router_id`` and ``router_region``
    router = resource.Body('router', type=Router)
    #: sequence serial of modified flag
    serial = resource.Body('serial', type=int)
    #: Zone status
    #: Valid values include ``PENDING_CREATE``, ``ACTIVE``,
    #:                       ``PENDING_DELETE``, ``ERROR``
    status = resource.Body('status')
    #: Recordset number of the zone
    record_num = resource.Body('record_num', type=int)
    #: The pool which manages the zone, assigned by system
    pool_id = resource.Body('pool_id')
    #: The project id which the zone belongs to
    project_id = resource.Body('project_id')
    #: Links contains a `self` pertaining to this zone or a `next` pertaining
    #: to next page
    links = resource.Body('links', type=dict)
    #: The master list for slaver server to fetch DNS
    masters = resource.Body('masters', type=list)
    #: Router list associated to this zone
    routers = resource.Body('routers', type=list)
    #: Timestamp when the zone was created
    created_at = resource.Body('created_at')
    #: Timestamp when the zone was last updated
    updated_at = resource.Body('updated_at')
