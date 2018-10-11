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


class Chassis(resource.Resource):

    resources_key = 'chassis'
    base_path = '/chassis'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True
    commit_method = 'PATCH'
    commit_jsonpatch = True

    _query_mapping = resource.QueryParameters(
        'fields'
    )

    #: Timestamp at which the chassis was created.
    created_at = resource.Body('created_at')
    #: A descriptive text about the service
    description = resource.Body('description')
    #: A set of one or more arbitrary metadata key and value pairs.
    extra = resource.Body('extra')
    #: The UUID for the chassis
    id = resource.Body('uuid', alternate_id=True)
    #: A list of relative links, including the self and bookmark links.
    links = resource.Body('links', type=list)
    #: Links to the collection of nodes contained in the chassis
    nodes = resource.Body('nodes', type=list)
    #: Timestamp at which the chassis was last updated.
    updated_at = resource.Body('updated_at')


class ChassisDetail(Chassis):

    base_path = '/chassis/detail'

    # capabilities
    allow_create = False
    allow_fetch = False
    allow_commit = False
    allow_delete = False
    allow_list = True

    #: The UUID for the chassis
    id = resource.Body('uuid', alternate_id=True)
