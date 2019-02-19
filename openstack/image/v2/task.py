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


class Task(resource.Resource):
    resources_key = 'tasks'
    base_path = '/tasks'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'type', 'status', 'sort_dir', 'sort_key'
    )

    #: The date and time when the task was created.
    created_at = resource.Body('created_at')
    #: The date and time when the task is subject to removal.
    expires_at = resource.Body('expires_at')
    #: A JSON object specifying the input parameters to the task.
    input = resource.Body('input')
    #: Human-readable text, possibly an empty string, usually displayed
    #: in an error situation to provide more information about what
    #: has occurred.
    message = resource.Body('message')
    #: The ID of the owner, or project, of the task.
    owner_id = resource.Body('owner')
    #: A JSON object specifying the outcome of the task.
    result = resource.Body('result')
    #: The URL for schema of the task.
    schema = resource.Body('schema')
    #: The status of the task.
    status = resource.Body('status')
    #: The type of task represented by this content.
    type = resource.Body('type')
    #: The date and time when the task was updated.
    updated_at = resource.Body('updated_at')
