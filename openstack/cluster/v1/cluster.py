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
from openstack import utils


class Cluster(resource.Resource):
    resource_key = 'cluster'
    resources_key = 'clusters'
    base_path = '/clusters'
    service = cluster_service.ClusterService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True
    patch_update = True

    # Properties
    #: The name of the cluster.
    name = resource.prop('name')
    #: The ID of the profile used by this cluster.
    profile_id = resource.prop('profile_id')
    #: The ID of the user who created this cluster, thus the owner of it.
    user = resource.prop('user')
    #: The ID of the project this cluster belongs to.
    project = resource.prop('project')
    #: The domain ID of the cluster owner.
    domain = resource.prop('domain')
    #: The ID of the parent cluster (if any).
    parent = resource.prop('parent')
    #: Timestamp of when the cluster was created.
    created_at = resource.prop('created_time')
    #: Timestamp of when the cluster was last updated.
    updated_at = resource.prop('updated_time')
    #: Timestamp of when the cluster was deleted. This is only used on
    #: clusters that were soft-deleted.
    deleted_at = resource.prop('deleted_time')
    #: Lower bound (inclusive) for the size of the cluster.
    min_size = resource.prop('min_size', type=int)
    #: Upper bound (inclusive) for the size of the cluster. A value of
    #: -1 indicates that there is no upper limit of cluster size.
    max_size = resource.prop('max_size', type=int)
    #: Desired capacity for the cluster. A cluster would be created at the
    #: scale specified by this value.
    desired_capacity = resource.prop('desired_capacity', type=int)
    #: Default timeout (in seconds) for cluster operations.
    timeout = resource.prop('timeout')
    #: A string representation of the cluster status.
    status = resource.prop('status')
    #: A string describing the reason why the cluster in current status.
    status_reason = resource.prop('status_reason')
    #: A collection of key-value pairs that are attached to the cluster.
    metadata = resource.prop('metadata', type=dict)
    #: A dictionary with some runtime data associated with the cluster.
    data = resource.prop('data', type=dict)
    #: A list IDs of nodes that are members of the cluster.
    nodes = resource.prop('nodes')
    #: Name of the profile used by the cluster.
    profile_name = resource.prop('profile_name')

    def action(self, session, body):
        url = utils.urljoin(self.base_path, self.id, 'actions')
        resp = session.post(url, endpoint_filter=self.service, json=body)
        return resp.json()

    def add_nodes(self, session, nodes):
        body = {
            'add_nodes': {
                'nodes': nodes,
            }
        }
        return self.action(session, body)

    def delete_nodes(self, session, nodes):
        body = {
            'del_nodes': {
                'nodes': nodes,
            }
        }
        return self.action(session, body)

    def scale_out(self, session, count=None):
        body = {
            'scale_out': {
                'count': count,
            }
        }
        return self.action(session, body)

    def scale_in(self, session, count=None):
        body = {
            'scale_in': {
                'count': count,
            }
        }
        return self.action(session, body)

    def policy_attach(self, session, policy_id, priority, level, cooldown,
                      enabled):
        body = {
            'policy_attach': {
                'policy_id': policy_id,
                'priority': priority,
                'level': level,
                'cooldown': cooldown,
                'enabled': enabled,
            }
        }
        return self.action(session, body)

    def policy_detach(self, session, policy_id):
        body = {
            'policy_detach': {
                'policy_id': policy_id,
            }
        }
        return self.action(session, body)

    def policy_update(self, session, policy_id, priority, level, cooldown,
                      enabled):

        body = {
            'policy_update': {
                'policy_id': policy_id,
            }
        }
        if priority is not None:
            body['policy_update']['priority'] = priority
        if level is not None:
            body['policy_update']['level'] = level
        if cooldown is not None:
            body['policy_update']['cooldown'] = cooldown
        if enabled is not None:
            body['policy_update']['enabled'] = enabled

        return self.action(session, body)

    def policy_enable(self, session, policy_id):
        body = {
            'policy_update': {
                'policy_id': policy_id,
                'enabled': True,
            }
        }
        return self.action(session, body)

    def policy_disable(self, session, policy_id):
        body = {
            'policy_update': {
                'policy_id': policy_id,
                'enabled': False,
            }
        }
        return self.action(session, body)
