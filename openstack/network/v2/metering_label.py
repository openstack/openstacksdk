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

from openstack import resource


class MeteringLabel(resource.Resource):
    resource_key = 'metering_label'
    resources_key = 'metering_labels'
    base_path = '/metering/metering-labels'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'description', 'name',
        is_shared='shared',
        project_id='tenant_id'
    )

    # Properties
    #: Description of the metering label.
    description = resource.Body('description')
    #: Name of the metering label.
    name = resource.Body('name')
    #: The ID of the project this metering label is associated with.
    project_id = resource.Body('tenant_id')
    #: Indicates whether this label is shared across all tenants.
    #: *Type: bool*
    is_shared = resource.Body('shared', type=bool)
