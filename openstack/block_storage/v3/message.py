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


class Message(resource.Resource):
    resource_key = "messages"
    resources_key = "messages"
    base_path = "/messages"

    _query_mapping = resource.QueryParameters(
        'project_id', 'sort', 'limit', 'offset', 'marker'
    )

    # capabilities
    allow_fetch = True
    allow_delete = True
    allow_list = True

    #: Properties
    #: The date and time when the resource was created.
    #: Format is ISO 8601: CCYY-MM-DDThh:mm:ss±hh:mm
    #: Example: 2015-08-27T09:49:58-05:00
    created_at = resource.Body("created_at", type=str)
    #: The id of the event to this message.
    event_id = resource.Body("event_id", type=str)
    #: The expire time of message, message could be deleted after this time.
    guaranteed_until = resource.Body("guaranteed_until", type=str)
    #: The level of the message, possible value is only 'ERROR' now.
    message_level = resource.Body("message_level", type=str)
    #: The id of the request during which the message was created.
    request_id = resource.Body("request_id", type=str)
    #: The resource type corresponding to resource_uuid.
    resource_type = resource.Body("resource_type", type=str)
    #: The UUID of the resource during whose operation the message was created.
    resource_uuid = resource.Body("resource_uuid", type=str)
    #: The translated readable message corresponding to event_id.
    user_message = resource.Body("user_message", type=str)
