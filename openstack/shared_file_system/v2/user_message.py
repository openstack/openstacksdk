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


class UserMessage(resource.Resource):
    resource_key = "message"
    resources_key = "messages"
    base_path = "/messages"

    # capabilities
    allow_fetch = True
    allow_commit = False
    allow_delete = True
    allow_list = True
    allow_head = False

    _query_mapping = resource.QueryParameters("message_id")

    _max_microversion = '2.37'

    #: Properties
    #: The action ID of the user message
    action_id = resource.Body("action_id", type=str)
    #: Indicate when the user message was created
    created_at = resource.Body("created_at", type=str)
    #: The detail ID of the user message
    detail_id = resource.Body("detail_id", type=str)
    #: Indicate when the share message expires
    expires_at = resource.Body("expires_at", type=str)
    #: The message level of the user message
    message_level = resource.Body("message_level", type=str)
    #: The project ID of the user message
    project_id = resource.Body("project_id", type=str)
    #: The request ID of the user message
    request_id = resource.Body("request_id", type=str)
    #: The resource ID of the user message
    resource_id = resource.Body("resource_id", type=str)
    #: The resource type of the user message
    resource_type = resource.Body("resource_type", type=str)
    #: The message for the user message
    user_message = resource.Body("user_message", type=str)
