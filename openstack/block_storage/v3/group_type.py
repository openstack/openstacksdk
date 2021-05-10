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


class GroupType(resource.Resource):
    resource_key = "group_type"
    resources_key = "group_types"
    base_path = "/group_types"

    # capabilities
    allow_fetch = True
    allow_create = True
    allow_delete = True
    allow_commit = True
    allow_list = True

    _max_microversion = "3.11"

    #: Properties
    #: The group type description.
    description = resource.Body("description")
    #: Contains the specifications for a group type.
    group_specs = resource.Body("group_specs", type=dict)
    #: Whether the group type is publicly visible.
    is_public = resource.Body("is_public", type=bool)
