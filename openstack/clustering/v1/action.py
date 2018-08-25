# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


from openstack import resource


class Action(resource.Resource):
    resource_key = 'action'
    resources_key = 'actions'
    base_path = '/actions'

    # Capabilities
    allow_list = True
    allow_fetch = True

    _query_mapping = resource.QueryParameters(
        'name', 'action', 'status', 'sort', 'global_project',
        target_id='target')

    # Properties
    #: Name of the action.
    name = resource.Body('name')
    #: ID of the target object, which can be a cluster or a node.
    target_id = resource.Body('target')
    #: Built-in type name of action.
    action = resource.Body('action')
    #: A string representation of the reason why the action was created.
    cause = resource.Body('cause')
    #: The owning engine that is currently running the action.
    owner_id = resource.Body('owner')
    #: The ID of the user who created this action.
    user_id = resource.Body('user')
    #: The ID of the project this profile belongs to.
    project_id = resource.Body('project')
    #: The domain ID of the action.
    domain_id = resource.Body('domain')
    #: Interval in seconds between two consecutive executions.
    interval = resource.Body('interval')
    #: The time the action was started.
    start_at = resource.Body('start_time')
    #: The time the action completed execution.
    end_at = resource.Body('end_time')
    #: The timeout in seconds.
    timeout = resource.Body('timeout')
    #: Current status of the action.
    status = resource.Body('status')
    #: A string describing the reason that brought the action to its current
    #  status.
    status_reason = resource.Body('status_reason')
    #: A dictionary containing the inputs to the action.
    inputs = resource.Body('inputs', type=dict)
    #: A dictionary containing the outputs to the action.
    outputs = resource.Body('outputs', type=dict)
    #: A list of actions that must finish before this action starts execution.
    depends_on = resource.Body('depends_on', type=list)
    #: A list of actions that can start only after this action has finished.
    depended_by = resource.Body('depended_by', type=list)
    #: Timestamp when the action is created.
    created_at = resource.Body('created_at')
    #: Timestamp when the action was last updated.
    updated_at = resource.Body('updated_at')
