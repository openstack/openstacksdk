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
from openstack import resource2 as resource


class Event(resource.Resource):
    resource_key = 'event'
    resources_key = 'events'
    base_path = '/events'
    service = cluster_service.ClusterService()

    # Capabilities
    allow_list = True
    allow_get = True

    _query_mapping = resource.QueryParameters(
        'cluster_id', 'action', 'level', 'sort', 'global_project',
        obj_id='oid', obj_name='oname', obj_type='otype',
    )

    # Properties
    #: Timestamp string (in ISO8601 format) when the event was generated.
    generated_at = resource.Body('timestamp')
    #: The UUID of the object related to this event.
    obj_id = resource.Body('oid')
    #: The name of the object related to this event.
    obj_name = resource.Body('oname')
    #: The type name of the object related to this event.
    obj_type = resource.Body('otype')
    #: The UUID of the cluster related to this event, if any.
    cluster_id = resource.Body('cluster_id')
    #: The event level (priority).
    level = resource.Body('level')
    #: The ID of the user.
    user_id = resource.Body('user')
    #: The ID of the project (tenant).
    project_id = resource.Body('project')
    #: The string representation of the action associated with the event.
    action = resource.Body('action')
    #: The status of the associated object.
    status = resource.Body('status')
    #: A string description of the reason that brought the object into its
    #: current status.
    status_reason = resource.Body('status_reason')
