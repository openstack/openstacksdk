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


class InspectionRule(resource.Resource):
    resources_key = 'inspection_rules'
    base_path = '/inspection_rules'

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

    # Inspection rules is available since 1.96
    _max_microversion = '1.96'
    #: The actions to be executed when the rule conditions are met.
    actions = resource.Body('actions', type=list)
    #: A brief explanation about the inspection rule.
    description = resource.Body('description')
    #: The conditions under which the rule should be triggered.
    conditions = resource.Body('conditions', type=list)
    #: Timestamp at which the resource was created.
    created_at = resource.Body('created_at')
    #: A list of relative links. Includes the self and bookmark links.
    links = resource.Body('links', type=list)
    #: Specifies the phase when the rule should run, defaults to 'main'.
    phase = resource.Body('phase')
    #: Specifies the rule's precedence level during execution.
    priority = resource.Body('priority')
    #: Indicates whether the rule contains sensitive information.
    sensitive = resource.Body('sensitive', type=bool)
    #: Timestamp at which the resource was last updated.
    updated_at = resource.Body('updated_at')
    #: The UUID of the resource.
    id = resource.Body('uuid', alternate_id=True)
