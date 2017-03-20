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
from openstack import resource2 as resource


class StackTemplate(resource.Resource):

    service = orchestration_service.OrchestrationService()
    base_path = "/stacks/%(stack_name)s/%(stack_id)s/template"

    # capabilities
    allow_create = False
    allow_list = False
    allow_get = True
    allow_delete = False
    allow_update = False

    # Properties
    #: Name of the stack where the template is referenced.
    stack_name = resource.URI('stack_name')
    #: ID of the stack where the template is referenced.
    stack_id = resource.URI('stack_id')
    #: The description specified in the template
    description = resource.Body('Description')
    #: The version of the orchestration HOT template.
    heat_template_version = resource.Body('heat_template_version')
    #: Key and value that contain output data.
    outputs = resource.Body('outputs', type=dict)
    #: Key and value pairs that contain template parameters
    parameters = resource.Body('parameters', type=dict)
    #: Key and value pairs that contain definition of resources in the
    #: template
    resources = resource.Body('resources', type=dict)
