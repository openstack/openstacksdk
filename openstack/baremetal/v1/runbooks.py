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

from openstack.baremetal.v1 import _common
from openstack import resource


class Runbook(_common.Resource):
    resources_key = 'runbooks'
    base_path = '/runbooks'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True
    allow_patch = True
    commit_method = 'PATCH'
    commit_jsonpatch = True

    _query_mapping = resource.QueryParameters(
        'detail',
        fields={'type': _common.fields_type},
    )

    # Runbooks is available since 1.92
    _max_microversion = '1.92'
    name = resource.Body('name')
    #: Timestamp at which the runbook was created.
    created_at = resource.Body('created_at')
    #: A set of one or more arbitrary metadata key and value pairs.
    extra = resource.Body('extra')
    #: A list of relative links. Includes the self and bookmark links.
    links = resource.Body('links', type=list)
    #: A set of physical information of the runbook.
    steps = resource.Body('steps', type=list)
    #: Indicates whether the runbook is publicly accessible.
    public = resource.Body('public', type=bool)
    #: The name or ID of the project that owns the runbook.
    owner = resource.Body('owner', type=str)
    #: Timestamp at which the runbook was last updated.
    updated_at = resource.Body('updated_at')
    #: The UUID of the resource.
    id = resource.Body('uuid', alternate_id=True)
