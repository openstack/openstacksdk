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


class ArchivePolicy(resource.Resource):
    base_path = '/archive_policy'
    service = metric_service.MetricService()

    # Supported Operations
    allow_create = True
    allow_get = True
    allow_delete = True
    allow_list = True

    # Properties
    #: The name of this policy
    name = resource.Body('name', alternate_id=True)
    #: The definition of this policy
    definition = resource.Body('definition', type=list)
    #: The window of time older than the period that archives can be requested
    back_window = resource.Body('back_window')
    #: A list of the aggregation methods supported
    aggregation_methods = resource.Body("aggregation_methods", type=list)
