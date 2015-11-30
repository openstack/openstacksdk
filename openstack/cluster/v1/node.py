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


class Node(resource.Resource):
    resource_key = 'node'
    resources_key = 'nodes'
    base_path = '/nodes'
    service = cluster_service.ClusterService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True

    patch_update = True

    # Properties
    #: The name of the node.
    name = resource.prop('name')
    #: The ID of the physical object that backs the node.
    physical_id = resource.prop('physical_id')
    #: The ID of the cluster in which this node is a member.
    #: A node is an orphan node if this field is empty.
    cluster_id = resource.prop('cluster_id')
    #: The ID of the profile used by this node.
    profile_id = resource.prop('profile_id')
    #: The ID of the project this node belongs to.
    project = resource.prop('project')
    #: The name of the profile used by this node.
    profile_name = resource.prop('profile_name')
    #: An integer that is unique inside the owning cluster.
    #: A value of -1 means this node is an orphan node.
    index = resource.prop('index', type=int)
    #: A string indicating the role the node plays in a cluster.
    role = resource.prop('role')
    #: The timestamp of the node object's initialization.
    init_time = resource.prop('init_time')
    #: The timestamp of the node's creation, i.e. the physical object
    #: represented by this node is also created.
    created_time = resource.prop('created_time')
    #: The timestamp the node was last updated.
    updated_time = resource.prop('updated_time')
    #: The timestamp the node was deleted. This is only used for node
    #: which has been soft deleted.
    deleted_time = resource.prop('deleted_time')
    #: A string indicating the node's status.
    status = resource.prop('status')
    #: A string describing why the node entered its current status.
    status_reason = resource.prop('status_reason')
    #: A map containing key-value pairs attached to the node.
    metadata = resource.prop('tags', type=dict)
    #: A map containing some runtime data for this node.
    data = resource.prop('data', type=dict)
    #: A map containing the details of the physical object this node
    #: represents
    details = resource.prop('details', type=dict)

    def _action(self, session, body):
        """Procedure the invoke an action API.

        :param session: A session object used for sending request.
        :param body: The body of action to be sent.
        """
        url = utils.urljoin(self.base_path, self.id, 'actions')
        resp = session.post(url, endpoint_filter=self.service, json=body)
        return resp.json()

    def join(self, session, cluster_id):
        """An action procedure for the node to join a cluster.

        :param session: A session object used for sending request.
        :param cluster_id: The ID, name or short ID of a cluster the
            node is about to join.
        :returns: A dictionary containing the action ID.
        """
        body = {
            'join': {
                'cluster_id': cluster_id,
            }
        }
        return self._action(session, body)

    def leave(self, session):
        """An action procedure for the node to leave its current cluster.

        :param session: A session object used for sending request.
        :returns: A dictionary containing the action ID.
        """
        body = {
            'leave': {}
        }
        return self._action(session, body)
