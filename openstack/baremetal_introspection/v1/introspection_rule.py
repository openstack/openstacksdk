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


class IntrospectionRule(resource.Resource):
    resources_key = 'rules'
    base_path = '/rules'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = False
    allow_delete = True
    allow_list = True

    # created via POST with ID
    create_method = 'POST'
    create_requires_id = True

    #: The UUID of the resource.
    id = resource.Body('uuid', alternate_id=True)
    #: List of a logic statementd or operations in rules
    conditions = resource.Body('conditions', type=list)
    #: List of operations that will be performed if conditions of this rule
    #: are fulfilled.
    actions = resource.Body('actions', type=list)
    #: Rule human-readable description
    description = resource.Body('description')
    #: Scope of an introspection rule
    scope = resource.Body('scope')
    #: A list of relative links, including the self and bookmark links.
    links = resource.Body('links', type=list)
