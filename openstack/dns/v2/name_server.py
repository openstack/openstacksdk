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


class NameServer(resource.Resource):
    resource_key = 'nameserver'
    resources_key = 'nameservers'
    base_path = '/zones/%(zone_id)s/nameservers'
    service = dns_service.DNSService()

    # capabilities
    allow_create = False
    allow_list = True
    allow_get = False
    allow_delete = False

    #: Properties
    #: The ID of zone using this name-server
    zone_id = resource.URI('zone_id')
    #: NameServer priority
    priority = resource.Body('priority')
    #: NameServer private DNS address
    address = resource.Body('address')
    #: NameServer public DNS address
    hostname = resource.Body('hostname')
