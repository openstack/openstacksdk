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

from openstack.metric import metric_service
from openstack import resource2 as resource


class Generic(resource.Resource):
    base_path = '/resource/generic'
    service = metric_service.MetricService()

    # Supported Operations
    allow_create = True
    allow_get = True
    allow_delete = True
    allow_list = True
    allow_update = True

    # Properties
    #: The identifier of this resource
    id = resource.Body('id')
    #: The ID of the user who created this resource
    created_by_user_id = resource.Body('created_by_user_id')
    #: The ID of the project this resource was created under
    created_by_project_id = resource.Body('created_by_project_id')
    #: The ID of the user
    user_id = resource.Body('user_id')
    #: The ID of the project
    project_id = resource.Body('project_id')
    #: Timestamp when this resource was started
    started_at = resource.Body('started_at')
    #: Timestamp when this resource was ended
    ended_at = resource.Body('ended_at')
    #: A dictionary of metrics collected on this resource
    metrics = resource.Body('metrics', type=dict)
    #: The type of resource
    type = resource.Body('type')
