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


class Event(resource.Resource):
    resource_key = 'event'
    resources_key = 'events'
    base_path = '/events'
    service = cluster_service.ClusterService()

    # Capabilities
    allow_list = True
    allow_retrieve = True

    # Properties
    id = resource.prop('id')
    timestamp = resource.prop('timestamp', type=format.ISO8601)
    obj_id = resource.prop('obj_id')
    obj_name = resource.prop('obj_name')
    obj_type = resource.prop('obj_type')
    cluster_id = resource.prop('cluster_id')
    level = resource.prop('level')
    user_id = resource.prop('user')
    project_id = resource.prop('project')
    action = resource.prop('action')
    status = resource.prop('status')
    status_reason = resource.prop('status_reason')
