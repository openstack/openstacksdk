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


class StackEvent(resource.Resource):
    base_path = '/stacks/%(stack_name)s/%(stack_id)s/events'
    resources_key = 'events'

    # capabilities
    allow_create = False
    allow_list = True
    allow_fetch = True
    allow_delete = False
    allow_commit = False

    _query_mapping = resource.QueryParameters(
        "resource_action",
        "resource_status",
        "resource_name",
        "resource_type",
        "nested_depth",
        "sort_key",
        "sort_dir",
    )

    # Properties
    #: The date and time when the event was created
    event_time = resource.Body('event_time')
    #: The ID of the event object
    id = resource.Body('id')
    #: A list of dictionaries containing links relevant to the stack.
    links = resource.Body('links')
    #: The ID of the logical stack resource.
    logical_resource_id = resource.Body('logical_resource_id')
    #: The ID of the stack physical resource.
    physical_resource_id = resource.Body('physical_resource_id')
    #: The name of the resource.
    resource_name = resource.Body('resource_name')
    #: The status of the resource.
    resource_status = resource.Body('resource_status')
    #: The reason for the current stack resource state.
    resource_status_reason = resource.Body('resource_status_reason')
