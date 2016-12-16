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

from openstack.bare_metal import bare_metal_service
from openstack import resource2 as resource


class Driver(resource.Resource):

    resources_key = 'drivers'
    base_path = '/drivers'
    service = bare_metal_service.BareMetalService()

    # capabilities
    allow_create = False
    allow_get = True
    allow_update = False
    allow_delete = False
    allow_list = True

    # NOTE: Query mapping?

    #: The name of the driver
    name = resource.Body('name', alternate_id=True)
    #: A list of active hosts that support this driver.
    hosts = resource.Body('hosts', type=list)
    #: A list of relative links, including the self and bookmark links.
    links = resource.Body('links', type=list)
    #: A list of links to driver properties.
    properties = resource.Body('properties', type=list)
