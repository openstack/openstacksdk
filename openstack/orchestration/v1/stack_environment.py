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


class StackEnvironment(resource.Resource):

    service = orchestration_service.OrchestrationService()
    base_path = "/stacks/%(stack_name)s/%(stack_id)s/environment"

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
    #: A list of parameter names whose values are encrypted
    encrypted_param_names = resource.Body('encrypted_param_names')
    #: A list of event sinks
    event_sinks = resource.Body('event_sinks')
    #: A map of parameters and their default values defined for the stack.
    parameter_defaults = resource.Body('parameter_defaults')
    #: A map of parametes defined in the stack template.
    parameters = resource.Body('parameters', type=dict)
    #: A map containing customized resource definitions.
    resource_registry = resource.Body('resource_registry', type=dict)
