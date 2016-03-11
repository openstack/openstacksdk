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

from openstack.compute import compute_service
from openstack import format
from openstack import resource


class Extension(resource.Resource):
    resource_key = 'extension'
    resources_key = 'extensions'
    base_path = '/extensions'
    service = compute_service.ComputeService()
    id_attribute = "alias"

    # capabilities
    allow_retrieve = True
    allow_list = True

    # Properties
    #: A short name by which this extension is also known.
    alias = resource.prop('alias')
    #: Text describing this extension's purpose.
    description = resource.prop('description')
    #: Links pertaining to this extension. This is a list of dictionaries,
    #: each including keys ``href`` and ``rel``.
    links = resource.prop('links')
    #: The name of the extension.
    name = resource.prop('name')
    #: A URL pointing to the namespace for this extension.
    namespace = resource.prop('namespace')
    #: Timestamp when this extension was last updated.
    #: *Type: datetime object parsed from ISO 8601 formatted string*
    updated_at = resource.prop('updated', type=format.ISO8601)
