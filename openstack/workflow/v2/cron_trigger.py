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


class CronTrigger(resource.Resource):
    resource_key = 'cron_trigger'
    resources_key = 'cron_triggers'
    base_path = '/cron_triggers'

    # capabilities
    allow_create = True
    allow_list = True
    allow_fetch = True
    allow_delete = True

    _query_mapping = resource.QueryParameters(
        'marker',
        'limit',
        'sort_keys',
        'sort_dirs',
        'fields',
        'name',
        'workflow_name',
        'workflow_id',
        'workflow_input',
        'workflow_params',
        'scope',
        'pattern',
        'remaining_executions',
        'project_id',
        'first_execution_time',
        'next_execution_time',
        'created_at',
        'updated_at',
        'all_projects',
    )

    #: The name of this Cron Trigger
    name = resource.Body("name")
    #: The pattern for this Cron Trigger
    pattern = resource.Body("pattern")
    #: Count of remaining exectuions
    remaining_executions = resource.Body("remaining_executions")
    #: Time of the first execution
    first_execution_time = resource.Body("first_execution_time")
    #: Time of the next execution
    next_execution_time = resource.Body("next_execution_time")
    #: Workflow name
    workflow_name = resource.Body("workflow_name")
    #: Workflow ID
    workflow_id = resource.Body("workflow_id")
    #: The inputs for Workflow
    workflow_input = resource.Body("workflow_input")
    #: Workflow params
    workflow_params = resource.Body("workflow_params")
    #: The ID of the associated project
    project_id = resource.Body("project_id")
    #: The time at which the cron trigger was created
    created_at = resource.Body("created_at")
    #: The time at which the cron trigger was created
    updated_at = resource.Body("updated_at")

    def create(
        self,
        session,
        prepend_key=False,
        *args,
        **kwargs,
    ):
        return super().create(session, prepend_key, *args, **kwargs)
