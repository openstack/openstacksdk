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

    _allow_unknown_attrs_in_body = True

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'description',
        'name',
        'project_id',
        'sort_key',
        'sort_dir',
        is_shared='shared',
    )

    # Properties
    #: Description of the metering label.
    description = resource.Body('description')
    #: Name of the metering label.
    name = resource.Body('name')
    #: The ID of the project this metering label is associated with.
    project_id = resource.Body('project_id', alias='tenant_id')
    #: Tenant_id (deprecated attribute).
    tenant_id = resource.Body('tenant_id', deprecated=True)
    #: Indicates whether this label is shared across all tenants.
    #: *Type: bool*
    is_shared = resource.Body('shared', type=bool)
