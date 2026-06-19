# Copyright 2026 Openinfra Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from openstack import resource


class ServerExternalEvent(resource.Resource):
    resource_key = None
    resources_key = 'events'
    base_path = '/os-server-external-events'
    requires_id = False
    create_requires_id = False

    # capabilities
    allow_create = True
    allow_fetch = False
    allow_delete = False
    allow_list = False
    allow_commit = False

    # Properties
    #: The name of this event
    name = resource.Body('name')
    # The UUID of the server instance to which the API dispatches the event.
    server_uuid = resource.Body('server_uuid')
    # The status of the event (optional)The event status.
    # A valid value is failed, completed, or in-progress.
    status = resource.Body('status')
    # A string value that identifies the event.
    tag = resource.Body('tag')
    #: The result code (set in the response)
    code = resource.Body('code', type=int)
