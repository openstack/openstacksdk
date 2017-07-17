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


class PTR(resource.Resource):
    """DNS reverse record resource"""
    resources_key = 'floatingips'
    base_path = '/reverse/floatingips'
    service = dns_service.DNSService()

    # capabilities
    allow_create = True
    allow_get = True
    allow_update = True
    allow_list = True
    patch_update = True

    #: Properties
    #: Region
    region = resource.Body('region')
    #: Floating IP ID
    floating_ip_id = resource.Body('floatingip_id')
    #: PTR domain name
    ptrdname = resource.Body('ptrdname')
    #: Recordset description
    description = resource.Body('description')
    #: Time to live, default 300, available value 300-2147483647 (seconds)
    ttl = resource.Body('ttl', type=int)
    #: Ip address
    address = resource.Body('address')
    #: The PTR record status
    status = resource.Body('status')
    #: Is the recordset created by system.
    action = resource.Body('action')
    #: Links contains a `self` pertaining to this zone or a `next` pertaining
    #: to next page
    links = resource.Body('links', type=dict)
