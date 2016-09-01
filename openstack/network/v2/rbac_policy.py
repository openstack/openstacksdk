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

from openstack.network import network_service
from openstack import resource2 as resource


class RBACPolicy(resource.Resource):
    resource_key = 'rbac_policy'
    resources_key = 'rbac_policies'
    base_path = '/rbac-policies'
    service = network_service.NetworkService()

    # capabilities
    allow_create = True
    allow_get = True
    allow_update = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'action', 'object_id', 'object_type', 'project_id',
        'target_project_id',
    )

    # Properties
    #: ID of the object that this RBAC policy affects.
    object_id = resource.Body('object_id')
    #: The ID of the project this RBAC will be enforced.
    target_project_id = resource.Body('target_tenant')
    #: The owner project ID.
    project_id = resource.Body('tenant_id')
    #: Type of the object that this RBAC policy affects.
    object_type = resource.Body('object_type')
    #: Action for the RBAC policy.
    action = resource.Body('action')
