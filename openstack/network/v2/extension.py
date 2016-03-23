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

from openstack import format
from openstack.network import network_service
from openstack import resource


class Extension(resource.Resource):
    resource_key = 'extension'
    resources_key = 'extensions'
    base_path = '/extensions'
    service = network_service.NetworkService()
    id_attribute = "alias"

    # capabilities
    allow_retrieve = True
    allow_list = True

    # Properties
    #: An alias the extension is known under.
    alias = resource.prop('alias')
    #: Text describing what the extension does.
    description = resource.prop('description')
    #: Links pertaining to this extension.
    links = resource.prop('links')
    #: The name of this extension.
    name = resource.prop('name')
    #: A URL pointing to the namespace for this extension.
    namespace = resource.prop('namespace')
    #: Timestamp when the extension was last updated.
    #: *Type: datetime object parsed from ISO 8601 formatted string*
    updated_at = resource.prop('updated', type=format.ISO8601)
