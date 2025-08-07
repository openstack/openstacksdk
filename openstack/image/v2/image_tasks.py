# Copyright 2024 RedHat Inc.
# All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

from openstack import resource


class ImageTasks(resource.Resource):
    resources_key = 'tasks'
    base_path = '/images/%(image_id)s/tasks'

    allow_list = True

    _max_microversion = '2.17'

    #: The type of task represented by this content
    type = resource.Body('type')
    #: The current status of this task. The value can be pending, processing,
    #: success or failure
    status = resource.Body('status')
    #: An identifier for the owner of the task, usually the tenant ID
    owner = resource.Body('owner')
    #: The date and time when the task is subject to removal (ISO8601 format)
    expires_at = resource.Body('expires_at')
    #: The date and time when the task was created (ISO8601 format)
    created_at = resource.Body('created_at')
    #: The date and time when the task was updated (ISO8601 format)
    updated_at = resource.Body('updated_at')
    #: The date and time when the task was deleted (ISO8601 format)
    deleted_at = resource.Body('deleted_at')
    #: Whether the task was deleted
    deleted = resource.Body('deleted')
    #: The ID of the image associated to this task
    image_id = resource.Body('image_id')
    #: The request ID of the user message
    request_id = resource.Body('request_id')
    #: The user id associated with this task
    user_id = resource.Body('user_id')
    #: A JSON object specifying the input parameters to the task
    input = resource.Body('input')
    #: A JSON object specifying information about the ultimate outcome of the
    #: task
    result = resource.Body('result')
    #: Human-readable text, possibly an empty string, usually displayed in a
    #: error situation to provide more information about what has occurred
    message = resource.Body('message')
