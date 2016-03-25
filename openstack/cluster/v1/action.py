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


from openstack.cluster import cluster_service
from openstack import format
from openstack import resource


class Action(resource.Resource):
    resource_key = 'action'
    resources_key = 'actions'
    base_path = '/actions'
    service = cluster_service.ClusterService()

    # Capabilities
    allow_list = True
    allow_retrieve = True

    # Properties
    #: Name of the action.
    name = resource.prop('name')
    #: ID of the target object, which can be a cluster or a node.
    target_id = resource.prop('target')
    #: Built-in type name of action.
    action = resource.prop('action')
    #: A string representation of the reason why the action was created.
    cause = resource.prop('cause')
    #: The owning engine that is currently running the action.
    owner_id = resource.prop('owner')
    #: Interval in seconds between two consecutive executions.
    interval = resource.prop('interval')
    #: The time the action was started.
    #: *Type: datetime object parsed from a UNIX epoch*
    start_at = resource.prop('start_time', type=format.UNIXEpoch)
    #: The time the action completed execution.
    #: *Type: datetime object parsed from a UNIX epoch*
    end_at = resource.prop('end_time', type=format.UNIXEpoch)
    #: The timeout in seconds.
    timeout = resource.prop('timeout')
    #: Current status of the action.
    status = resource.prop('status')
    #: A string describing the reason that brought the action to its current
    #  status.
    status_reason = resource.prop('status_reason')
    #: A dictionary containing the inputs to the action.
    inputs = resource.prop('inputs', type=dict)
    #: A dictionary containing the outputs to the action.
    outputs = resource.prop('outputs', type=dict)
    #: A list of actions that must finish before this action starts execution.
    depends_on = resource.prop('depends_on', type=list)
    #: A list of actions that can start only after this action has finished.
    depended_by = resource.prop('depended_by', type=list)
    #: Timestamp when the action is created.
    #: *Type: datetime object parsed from ISO 8601 formatted string*
    created_at = resource.prop('created_at', type=format.ISO8601)
    #: Timestamp when the action was last updated.
    #: *Type: datetime object parsed from ISO 8601 formatted string*
    updated_at = resource.prop('updated_at', type=format.ISO8601)
