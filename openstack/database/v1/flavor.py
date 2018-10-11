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

from openstack import resource


class Flavor(resource.Resource):
    resource_key = 'flavor'
    resources_key = 'flavors'
    base_path = '/flavors'

    # capabilities
    allow_list = True
    allow_fetch = True

    # Properties
    #: Links associated with the flavor
    links = resource.Body('links')
    #: The name of the flavor
    name = resource.Body('name')
    #: The size in MB of RAM the flavor has
    ram = resource.Body('ram')
