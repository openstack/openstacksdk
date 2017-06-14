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

from openstack.cluster import cluster_service
from openstack import resource2 as resource


class Receiver(resource.Resource):
    resource_key = 'receiver'
    resources_key = 'receivers'
    base_path = '/receivers'
    service = cluster_service.ClusterService()

    # Capabilities
    allow_list = True
    allow_get = True
    allow_create = True
    allow_update = True
    allow_delete = True

    patch_update = True

    _query_mapping = resource.QueryParameters(
        'name', 'type', 'cluster_id', 'action', 'sort', 'global_project',
        user_id='user')

    # Properties
    #: The name of the receiver.
    name = resource.Body('name')
    #: The type of the receiver.
    type = resource.Body('type')
    #: The ID of the user who created the receiver, thus the owner of it.
    user_id = resource.Body('user')
    #: The ID of the project this receiver belongs to.
    project_id = resource.Body('project')
    #: The domain ID of the receiver.
    domain_id = resource.Body('domain')
    #: The ID of the targeted cluster.
    cluster_id = resource.Body('cluster_id')
    #: The name of the targeted action.
    action = resource.Body('action')
    #: Timestamp of when the receiver was created.
    created_at = resource.Body('created_at')
    #: Timestamp of when the receiver was last updated.
    updated_at = resource.Body('updated_at')
    #: The credential of the impersonated user.
    actor = resource.Body('actor', type=dict)
    #: A dictionary containing key-value pairs that are provided to the
    #: targeted action.
    params = resource.Body('params', type=dict)
    #: The information about the channel through which you can trigger the
    #: receiver hence the associated action.
    channel = resource.Body('channel', type=dict)
