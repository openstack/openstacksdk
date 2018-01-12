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

from openstack.network import network_service
from openstack import resource


class Extension(resource.Resource):
    resource_key = 'extension'
    resources_key = 'extensions'
    base_path = '/extensions'
    service = network_service.NetworkService()

    # capabilities
    allow_get = True
    allow_list = True

    # NOTE: No query parameters supported

    # Properties
    #: An alias the extension is known under.
    alias = resource.Body('alias', alternate_id=True)
    #: Text describing what the extension does.
    description = resource.Body('description')
    #: Links pertaining to this extension.
    links = resource.Body('links')
    #: The name of this extension.
    name = resource.Body('name')
    #: Timestamp when the extension was last updated.
    updated_at = resource.Body('updated')
