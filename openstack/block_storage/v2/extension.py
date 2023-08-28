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


class Extension(resource.Resource):
    resources_key = "extensions"
    base_path = "/extensions"

    # Capabilities
    allow_list = True

    #: Properties
    #: The alias for the extension.
    alias = resource.Body('alias', type=str)
    #: The extension description.
    description = resource.Body('description', type=str)
    #: Links pertaining to this extension.
    links = resource.Body('links', type=list)
    #: The name of this extension.
    name = resource.Body('name')
    #: A URL pointing to the namespace for this extension.
    namespace = resource.Body('namespace')
    #: The date and time when the resource was updated.
    #: The date and time stamp format is ISO 8601.
    updated_at = resource.Body('updated', type=str)
