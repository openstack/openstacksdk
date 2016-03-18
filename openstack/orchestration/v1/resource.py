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

from openstack import format
from openstack.orchestration import orchestration_service
from openstack import resource


class Resource(resource.Resource):
    name_attribute = 'resource_name'
    resource_key = 'resource'
    resources_key = 'resources'
    base_path = '/stacks/%(stack_name)s/%(stack_id)s/resources'
    service = orchestration_service.OrchestrationService()

    # capabilities
    allow_create = False
    allow_list = True
    allow_retrieve = False
    allow_delete = False
    allow_update = False

    # Properties
    #: A list of dictionaries containing links relevant to the resource.
    links = resource.prop('links')
    #: ID of the logical resource, usually the literal name of the resource
    #: as it appears in the stack template.
    logical_resource_id = resource.prop('logical_resource_id')
    #: Name of the resource.
    name = resource.prop('resource_name')
    #: ID of the physical resource (if any) that backs up the resource. For
    #: example, it contains a nova server ID if the resource is a nova
    #: server.
    physical_resource_id = resource.prop('physical_resource_id')
    #: A list of resource names that depend on this resource. This
    #: property facilitates the deduction of resource dependencies.
    #: *Type: list*
    required_by = resource.prop('required_by', type=list)
    #: A string representation of the resource type.
    resource_type = resource.prop('resource_type')
    #: A string representing the status the resource is currently in.
    status = resource.prop('resource_status')
    #: A string that explains why the resource is in its current status.
    status_reason = resource.prop('resource_status_reason')
    #: Timestamp of the last update made to the resource.
    #: *Type: datetime object parsed from ISO 8601 formatted string*
    updated_at = resource.prop('updated_time', type=format.ISO8601)
