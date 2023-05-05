# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from openstack import resource


class ServerActionEvent(resource.Resource):
    # Added the 'details' field in 2.84
    _max_microversion = '2.84'

    #: The name of the event
    event = resource.Body('event')
    #: The date and time when the event was started. The date and time stamp
    #: format is ISO 8601
    start_time = resource.Body('start_time')
    #: The date and time when the event finished. The date and time stamp
    #: format is ISO 8601
    finish_time = resource.Body('finish_time')
    #: The result of the event
    result = resource.Body('result')
    #: The traceback stack if an error occurred in this event.
    #: This is only visible to cloud admins by default.
    traceback = resource.Body('traceback')
    #: The name of the host on which the event occurred.
    #: This is only visible to cloud admins by default.
    host = resource.Body('host')
    #: An obfuscated hashed host ID string, or the empty string if there is no
    #: host for the event. This is a hashed value so will not actually look
    #: like a hostname, and is hashed with data from the project_id, so the
    #: same physical host as seen by two different project_ids will be
    #: different. This is useful when within the same project you need to
    #: determine if two events occurred on the same or different physical
    #: hosts.
    host_id = resource.Body('hostId')
    #: Details of the event. May be unset.
    details = resource.Body('details')


class ServerAction(resource.Resource):
    resource_key = 'instanceAction'
    resources_key = 'instanceActions'
    base_path = '/servers/%(server_id)s/os-instance-actions'

    # capabilities
    allow_fetch = True
    allow_list = True

    # Properties

    #: The ID of the server that this action relates to.
    server_id = resource.URI('server_id')

    #: The name of the action.
    action = resource.Body('action')
    # FIXME(stephenfin): This conflicts since there is a server ID in the URI
    # *and* in the body. We need a field that handles both or we need to use
    # different names.
    # #: The ID of the server that this action relates to.
    # server_id = resource.Body('instance_uuid')
    #: The ID of the request that this action related to.
    request_id = resource.Body('request_id', alternate_id=True)
    #: The ID of the user which initiated the server action.
    user_id = resource.Body('user_id')
    #: The ID of the project that this server belongs to.
    project_id = resource.Body('project_id')
    start_time = resource.Body('start_time')
    #: The related error message for when an action fails.
    message = resource.Body('message')
    #: Events
    events = resource.Body('events', type=list, list_type=ServerActionEvent)

    # events.details field added in 2.84
    _max_microversion = '2.84'

    _query_mapping = resource.QueryParameters(
        changes_since="changes-since",
        changes_before="changes-before",
    )
