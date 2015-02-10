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
from openstack import resource


class Metric(resource.Resource):
    base_path = '/metric'
    service = metric_service.MetricService()

    # Supported Operations
    allow_create = True
    allow_retrieve = True
    allow_delete = True
    allow_list = True

    # Properties
    archive_policy_name = resource.prop('archive_policy_name')
    archive_policy = resource.prop('archive_policy')
    created_by_user_id = resource.prop('created_by_user_id')
    created_by_project_id = resource.prop('created_by_project_id')
    resource_id = resource.prop('resource_id')
    name = resource.prop('name')
