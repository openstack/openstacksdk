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


class Metric(resource.Resource):
    base_path = '/metric'
    service = metric_service.MetricService()

    # Supported Operations
    allow_create = True
    allow_get = True
    allow_delete = True
    allow_list = True

    # Properties
    #: The name of the archive policy
    archive_policy_name = resource.Body('archive_policy_name')
    #: The archive policy
    archive_policy = resource.Body('archive_policy')
    #: The ID of the user who created this metric
    created_by_user_id = resource.Body('created_by_user_id')
    #: The ID of the project this metric was created under
    created_by_project_id = resource.Body('created_by_project_id')
    #: The identifier of this metric
    resource_id = resource.Body('resource_id')
    #: The name of this metric
    name = resource.Body('name')
