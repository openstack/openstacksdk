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


class MetadefSchema(resource.Resource):
    base_path = '/schemas/metadefs'

    # capabilities
    allow_fetch = True

    #: A boolean value that indicates allows users to add custom properties.
    additional_properties = resource.Body('additionalProperties', type=bool)
    #: A set of definitions.
    definitions = resource.Body('definitions', type=dict)
    #: A list of required resources.
    required = resource.Body('required', type=list)
    #: Schema properties.
    properties = resource.Body('properties', type=dict)
