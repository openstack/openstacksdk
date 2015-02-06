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

from openstack.orchestration import orchestration_service
from openstack import resource


class Stack(resource.Resource):
    resource_key = 'stack'
    resources_key = 'stacks'
    base_path = '/stacks'
    service = orchestration_service.OrchestrationService()

    # capabilities
    # NOTE(thowe): Special handling for other operations
    allow_list = True
    allow_retrieve = True

    # Properties
    name = resource.prop('stack_name')
    capabilities = resource.prop('capabilities')
    creation_time = resource.prop('creation_time')
    description = resource.prop('description')
    disable_rollback = resource.prop('disable_rollback', type=bool)
    links = resource.prop('links')
    notification_topics = resource.prop('notification_topics')
    outputs = resource.prop('outputs')
    parameters = resource.prop('parameters', type=dict)
    stack_status = resource.prop('stack_status')
    stack_status_reason = resource.prop('stack_status_reason')
    template_description = resource.prop('template_description')
    timeout_mins = resource.prop('timeout_mins')
    updated_time = resource.prop('updated_time')
