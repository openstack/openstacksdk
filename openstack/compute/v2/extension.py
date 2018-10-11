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
    resource_key = 'extension'
    resources_key = 'extensions'
    base_path = '/extensions'
    id_attribute = "alias"

    # capabilities
    allow_fetch = True
    allow_list = True

    # Properties
    #: A short name by which this extension is also known.
    alias = resource.Body('alias', alternate_id=True)
    #: Text describing this extension's purpose.
    description = resource.Body('description')
    #: Links pertaining to this extension. This is a list of dictionaries,
    #: each including keys ``href`` and ``rel``.
    links = resource.Body('links')
    #: The name of the extension.
    name = resource.Body('name')
    #: A URL pointing to the namespace for this extension.
    namespace = resource.Body('namespace')
    #: Timestamp when this extension was last updated.
    updated_at = resource.Body('updated')
