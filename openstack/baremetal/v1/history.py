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

from openstack.baremetal.v1 import _common
from openstack import resource


class History(_common.Resource):
    resources_key = 'history'
    base_path = '/nodes/%(node_id)s/history'

    # capabilities
    allow_fetch = True
    allow_list = True

    _query_mapping = resource.QueryParameters('detail', 'sort_key', 'sort_dir')

    # NOTE: 1.78 is the API version in which node history can be retrieved;
    # 1.113 added the project field and 1.115 added state,
    # target_provision_state and duration_seconds to the detailed view
    _max_microversion = '1.115'

    # Properties
    #: The UUID of the history event
    id = resource.Body('uuid', alternate_id=True)
    #: The UTC date and time when the resource was created, ISO 8601 format.
    created_at = resource.Body('created_at')
    #: The UUID value representing the user who appears to have caused the
    #: recorded event.
    user = resource.Body('user')
    #: Severity indicator for the event being returned.
    severity = resource.Body('severity')
    #: The event message body which has been logged related to the node for
    #: this error.
    event = resource.Body('event')
    #: Short descriptive string to indicate where the error occurred.
    event_type = resource.Body('event_type')
    #: The hostname of this conductor.
    conductor = resource.Body('conductor')
    #: The UUID of the project of the user who caused the event. Only
    #: available in detailed responses from API version 1.113.
    project = resource.Body('project')
    #: The provision state of the node when the event was recorded. Only
    #: available in detailed responses from API version 1.115.
    state = resource.Body('state')
    #: The target provision state of the node when the event was recorded.
    #: Only available in detailed responses from API version 1.115.
    target_provision_state = resource.Body('target_provision_state')
    #: The duration in seconds of the operation the event describes. Only
    #: available in detailed responses from API version 1.115.
    duration_seconds = resource.Body('duration_seconds')
    #: The ID for the node.
    node_id = resource.URI('node_id')
