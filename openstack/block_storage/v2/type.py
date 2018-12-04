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


class Type(resource.Resource):
    resource_key = "volume_type"
    resources_key = "volume_types"
    base_path = "/types"

    # capabilities
    allow_fetch = True
    allow_create = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters("is_public")

    # Properties
    #: A ID representing this type.
    id = resource.Body("id")
    #: Name of the type.
    name = resource.Body("name")
    #: A dict of extra specifications. "capabilities" is a usual key.
    extra_specs = resource.Body("extra_specs", type=dict)
    #: a private volume-type. *Type: bool*
    is_public = resource.Body('os-volume-type-access:is_public', type=bool)
