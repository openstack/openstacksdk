# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from openstack.cluster import cluster_service
from openstack import resource


class ClusterPolicy(resource.Resource):
    id_attribute = 'policy_id'
    resource_key = 'cluster_policy'
    resources_key = 'cluster_policies'
    base_path = '/clusters/%(cluster_id)s/policies'
    service = cluster_service.ClusterService()

    # Capabilities
    allow_list = True
    allow_retrieve = True

    # Properties
    #: ID of the policy object.
    policy_id = resource.prop('policy_id')
    #: Name of the policy object.
    policy_name = resource.prop('policy_name')
    #: ID of the cluster object.
    cluster_id = resource.prop('cluster_id')
    #: Name of the cluster object.
    cluster_name = resource.prop('cluster_name')
    #: Type string of the policy.
    policy_type = resource.prop('policy_type')
    #: Whether the policy is enabled on the cluster. *Type: bool*
    is_enabled = resource.prop('enabled', type=bool)
    #: Data associated with the cluster-policy binding.
    data = resource.prop('data', type=dict)
